# This is a microphone listener that connects with Dialog Flow (and optionally Vosk)
# This listens to the microphone input, and when a peak is detected (hardcoded below) it will start recording.
# Once the audio volume subsides for long enough, recording is stopped and the sound generated is processed.
# Then the actions returned by dialogflow are carried out.

# A future improvement would be to monitor the ambient audio volume and listen for peaks

import numpy
import qi
import stk.runner
import stk.events
import stk.services
import stk.logging

import json
import os
import StringIO
import sys
import time
import uuid

# Determines how many times we wait for audio peaking before deciding the user has finished speaking.
LISTENING_RETRY_COUNT = 15

# The minimum audio peak to trigger a recording.
AUDIO_PEAK_THRESHOLD = 3500

# Cap at 10 seconds, speech rec gets funny after this.
MAX_RECORD_TIME = 10


def byteify(input):
    """
    Convert a dictionary from using Unicode strings to ASCII.
    This is unfortunately necessary so that naoqi plays nice with our JSON.

    https://stackoverflow.com/a/13105359/11265569
    :param input: The "Unicode dict"
    :return: The "ASCII dict"
    """
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


class ListenerService(object):
    """
    Audio processing module.
    Detect peaks in users voices, then record what they are saying to transmit it to Dialog Flow.
    """

    def __init__(self, qiapp):
        # STK Boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, 'uk.ac.rgu.ListenerService')

        # Project ID for dialog flow, populated later.
        self.google_project_id = None

        # Get robot memory so we can attach to some events
        self.mem = self.s.ALMemory

        # Get robot LEDs so we can control eye colour
        self.leds = self.s.ALLeds

        # Get Pepper's audio device
        self.audio_device = self.s.ALAudioDevice
        self.speaker_hook = None

        # Get the speech recognition module so we can disable it.
        self.speech = self.s.ALSpeechRecognition

        # Dialog Flow and Vosk
        self.dialogflow = self.s.DialogFlowAPI
        self.vosk = None  # initialized if vosk is enabled

        # Properties for voice detection and recording
        self.is_listening = False
        self.is_paused = False
        self.is_recording = False
        self.sound_file = None
        self.previous_data = None
        self.retries = LISTENING_RETRY_COUNT

        # Save a timestamp of when recording started to enforce a maximum length.
        self.record_start = None

        # Set a UUID for the session ID.
        # Ensures multiple bots can run the same agent and not have colliding contexts
        self.session_id = uuid.uuid4()

        # Package UUID for filesystem access
        self.package_uuid = None

        # Enable vosk api for transcription?
        self.vosk_api = False

        # Proxies for handling responses
        self.tts = self.s.ALTextToSpeech
        self.tablet = self.s.ALTabletService
        self.behavior_manager = self.s.ALBehaviorManager

        # Tell Choregraphe we're ready to rock 'n' roll!
        self.mem.raiseEvent('ListenerServiceStarted', True)        

    @qi.bind(returnType=qi.Void, paramsType=[qi.String, qi.String])
    def start_listening(self, google_project_id, package_uuid):
        # Save package uuid
        self.google_project_id = google_project_id
        self.package_uuid = package_uuid

        # Configure audio device. 16000 sample rate, 3 = Front Mic, 0 = no deinterlacing, we do that ourselves
        # TODO: Future: Might be worth investigating using a higher sample rate and filtering the audio channels.
        self.audio_device.setClientPreferences('ListenerService', 16000, 3, 0)

        # Subscribe to audio processing events
        self.audio_device.subscribe('ListenerService')

        # Disable speech recognition
        self.speech.pause(True)

        # Mark as listening
        self.is_listening = True

        # Hook the speaker so we don't listen to our own output.
        self.speaker_hook = self.audio_device.speakersPlaying.connect(self.speakers_playing)

        # Start dialogflow session
        self.dialogflow.begin_session(str(self.google_project_id), str(self.session_id), 'en-GB')

    @qi.bind(returnType=qi.Void, paramsType=[])
    def cleanup(self):
        """Use this to tidy up any event subscriptions and to resume the built-in text to speech."""
        # Turn speech recognition back on as normal
        self.speech.pause(False)

        # Unsubscribe from audio processing
        self.audio_device.unsubscribe('ListenerService')

        # Not listening
        self.is_listening = False

        self.audio_device.speakersPlaying.disconnect(self.speaker_hook)

        # End the dialog flow session.
        self.dialogflow.end_session()

    @qi.bind(returnType=qi.Void)
    def enable_vosk(self):
        """
        Enable the VOSK transcription API.
        This is experimental and underdeveloped and thus has some accuracy issues.
        However, if worked on more could produce better latency results.
        """
        self.vosk_api = True
        self.vosk = self.session.service('VoskClient')

    def speakers_playing(self, playing):
        """Callback for Audio Device speakers. Prevents Pepper listening to itself."""
        self.is_paused = playing

    @qi.nobind
    def begin_record(self, previous_sound_data):
        """Begin recording by initialising a buffer for audio and writing any previous data"""
        # Initialize some memory for us to record to
        # StringIO is used so that it can be passed through the naoqi broker without serialization issues
        self.sound_file = StringIO.StringIO()
        self.is_recording = True
        self.record_start = time.time()

        # Write the last frame of data too if we have it.
        if previous_sound_data is not None:
            self.sound_file.write(previous_sound_data[0].tostring())

        self.logger.info('Recording has started.')

    @qi.nobind
    def stop_record(self):
        """Stop recording, clear any previous data"""
        # Clear last saved data
        self.previous_data = None
        self.is_recording = False

    @qi.nobind
    def process_audio(self):
        """
        Process the recorded audio and send it to dialogflow for intent processing.
        If Vosk API is enabled, audio will be processed first then sent as text to dialogflow.
        Otherwise, audio data will be sent to dialogflow.
        """

        # Send buffer pointer back to the start
        self.sound_file.seek(0, os.SEEK_END)
        length = self.sound_file.tell()
        self.sound_file.seek(0)

        # Read all audio data into a single buffer and send it to dialogflow
        input_audio = self.sound_file.read(length)

        # Send to dialogflow
        response_json = None
        start = time.clock()
        if self.vosk_api:
            # Transcribe audio with vosk
            text = self.vosk.transcribe(input_audio)
            self.logger.info('Vosk heard %s' % text)

            # If we heard something, send it to google for processing.
            if text is not None and text != '':
                response_json = self.dialogflow.detect_intent_text(text)
        else:
            response_json = self.dialogflow.detect_intent_audio(input_audio)

        end = time.clock()
        self.logger.info("Request took %f" % (end - start))

        # Convert JSON string to object and process it.
        response = byteify(json.loads(response_json))
        if response is not None:
            self.handle_actions(response)

    # noinspection PyPep8Naming
    def processRemote(self, channels, samples, _timestamp, audio_buffer):
        """Callback for audio processing."""

        # If you are using inteleaved data, you'll want to use this commented block instead of just converting from a
        #interleaved_data = numpy.fromstring(str(audio_buffer), dtype=numpy.int16)  # Load from a string
        #sound_data = numpy.reshape(interleaved_data, (channels, samples), 'F')  # Split data by channels

        # Load the single-channel sound data.
        sound_data = numpy.fromstring(str(audio_buffer), dtype=numpy.int16)

        # Save this last frame in case next frame we begin recording
        self.previous_data = sound_data

        # If we ain't listening, don't process
        if self.is_paused:
            # Show that Pepper isn't listening.
            self.eyes_ignoring()
            if self.is_recording:
                self.stop_record()
            return

        # Calculate audio peak for speech detection
        peak = numpy.max(sound_data)

        # If we peak, reset the counter and start recording if we haven't
        if peak >= AUDIO_PEAK_THRESHOLD:
            # Reset the retry count. We use this to determine when the user finishes speaking.
            self.retries = LISTENING_RETRY_COUNT
            if not self.is_recording:
                self.logger.info('START')
                self.begin_record(self.previous_data)

        # If we are recording, knock the retry counter down and save this data.
        if self.is_recording:
            # Change eyes to indicate listening
            self.eyes_listening()

            self.retries -= 1
            #self.sound_file.write(sound_data[0].tostring())
            self.sound_file.write(sound_data.tostring())

            # Don't listen for too long
            if time.time() - self.record_start > MAX_RECORD_TIME:
                self.logger.warn('Sentence was too long.')
                self.stop_record()

            # User may have stopped speaking
            if self.retries <= 0:
                self.logger.info('Stopping')
                self.stop_record()

                # Pepper will likely not be listening while we process.
                self.eyes_ignoring()
                self.process_audio()
        else:
            # Change to indicate idling.
            self.eyes_idle()


    @qi.nobind
    def handle_actions(self, response):
        """
        Handle the actions of a dialogflow response
        :param response: The dialogflow response as a dict. Must be accessed as response[...]
        """

        # If we have no result, don't run.
        # This doesn't tend to happen but its a nice safeguard.
        if not 'queryResult' in response:
            return

        # Easy access to the query result.
        query_result = response['queryResult']

        # Iterate over the additional payloads
        if 'fulfillmentMessages' in query_result:
            for message in query_result['fulfillmentMessages']:
                # Handle custom payloads
                if 'payload' in message and 'action' in message['payload']:
                    payload = message['payload']
                    action = payload['action']
                    if action == 'show_url':

                        url = payload['url']

                        if not url.startswith('http'):
                            url = 'http://%s/apps/%s' % (self.tablet.robotIp(),
                                                     os.path.join(self.package_uuid,
                                                                  os.path.normpath(url).lstrip("\\/"))
                                                     .replace(os.path.sep, "/"))
                        
                        self.tablet.showWebview(url)

                    elif action == 'clear_tablet':

                        self.tablet.hideWebview()

                    elif action == 'behavior':

                        name = str(payload['behavior'])
                        self.logger.info('Attempt to start behaviour "%s"' % name)
                        try:
                            self.behavior_manager.stopBehavior(name)
                        except:
                            pass

                        try:
                            self.behavior_manager.runBehavior(str(name))
                        except Exception as ex:
                            self.logger.error('Failed to start "%s"' % name, ex)
                    
                    # TODO: If an application developer wants a "rich" event, add it here.
                    else:
                        # Pass a generic action "bang" event.
                        self.mem.raiseEvent('DialogFlowAction', str(action))

        # Say the fulfilment text
        if 'fulfillmentText' in query_result:
            self.tts.say(query_result['fulfillmentText'])

    @qi.nobind
    def eyes_listening(self):
        """Makes Pepper's eyes blue to indicate listening"""
        self.set_eyes(0, 0, 255)

    @qi.nobind
    def eyes_idle(self):
        """Makes Pepper's eyes white to indicate idling"""
        self.set_eyes(255, 255, 255)

    @qi.nobind
    def eyes_ignoring(self):
        """Makes Pepper's eyes red to indicate ignorance"""
        self.set_eyes(255, 0, 0)

    @qi.nobind
    def set_eyes(self, r, g, b):
        """Set Pepper's face LEDs"""
        self.leds.fadeRGB("FaceLeds", r / 255, g / 255, b / 255, 0)  # 0 seconds fade to not freeze our listener


if __name__ == "__main__":
    stk.runner.run_service(ListenerService)