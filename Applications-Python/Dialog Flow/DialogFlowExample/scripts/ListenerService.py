# This is a microphone listener that connects with Dialog Flow (and optionally Vosk)
# This listens to the microphone input, and when a peak is detected (hardcoded below) it will start recording.
# Once the audio volume subsides for long enough, recording is stopped and the sound generated is processed.
# Then the actions returned by dialogflow are carried out.

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging

import numpy

import json
import os
import StringIO
import sys
import time
import uuid

# Determines how many times we wait for audio peaking before deciding the user has finished speaking.
LISTENING_RETRY_COUNT = 15

# The minimum audio peak to trigger a recording.
AUDIO_PEAK_THRESHOLD = 4000

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

        # Get dialog flow and vosk modules.
        self.dialogflow = self.s.DialogFlowService
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

    # TODO: Is there a way to avoid needing a package_uuid passing in?
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

    # TODO: Ensure this is fully working as expected.
    def speakers_playing(self, playing):
        self.is_paused = playing
        if self.is_paused:
            self.eyes_ignoring()
        else:
            self.eyes_idle()

    @qi.nobind
    def begin_record(self, previous_sound_data):
        # Initialize a "memory file". I believe StringIO is used so that it can be passed through the naoqi broker
        # without serialization issues (numpy.int16)?
        self.sound_file = StringIO.StringIO()
        self.is_recording = True
        self.record_start = time.time()

        # Write the last frame of data too if we have it.
        if previous_sound_data is not None:
            self.sound_file.write(previous_sound_data[0].tostring())

        # Set eyes indicator TODO: Without lag please Pepper?
        self.eyes_listening()

        self.logger.info('Recording has started.')

    @qi.nobind
    def stop_record(self):
        # Clear last saved data
        self.previous_data = None
        self.is_recording = False

        # Clear eye indicator
        self.eyes_idle()

    @qi.nobind
    def process_audio(self):
        """
        Process the recorded audio and send it to dialogflow for intent processing.
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

        # TODO: It seems some of the data loss could be due to inefficiencies in this function?
        #       Worth further investigation..

        # Load the data by casting to an array of 16-bit ints.
        interleaved_data = numpy.fromstring(str(audio_buffer), dtype=numpy.int16)

        # Deinterleave the data by splitting by channel
        sound_data = numpy.reshape(interleaved_data, (channels, samples), 'F')

        # Save this last frame in case next frame we begin recording
        self.previous_data = sound_data

        # If we ain't listening, don't process
        if self.is_paused:
            if self.is_recording:
                self.stop_record()
            return

        # Calculate audio peak for speech detection
        peak = numpy.max(sound_data)

        # If we peak, reset the counter and start recording if we haven't
        # If we have, we reset the listen count.
        if peak >= AUDIO_PEAK_THRESHOLD:
            self.retries = LISTENING_RETRY_COUNT
            if not self.is_recording:
                self.logger.info('START')
                self.begin_record(self.previous_data)

        # If we are recording, knock the retry counter down and save this data.
        if self.is_recording:
            self.retries -= 1
            self.sound_file.write(sound_data[0].tostring())

        # If we've been recording too long, cut them short.
        if self.is_recording and time.time() - self.record_start > MAX_RECORD_TIME:
            self.logger.warn('Sentence was too long.')
            self.stop_record()
            # self.tts.say('Sorry, that sentence was too big. Could you try again?')

        # If the user has stopped speaking, process the audio
        if self.is_recording and self.retries <= 0:
            self.logger.info('Stopping')
            self.stop_record()
            self.process_audio()

    @qi.nobind
    def handle_actions(self, response):
        """
        Handle the actions of a dialogflow response
        :param response: The dialogflow response as a dict. Must be accessed as response[...]
        """

        query_result = response['queryResult']

        # Iterate over the additional payloads
        if 'fulfillmentMessages' in query_result:
            for message in query_result['fulfillmentMessages']:
                # Handle custom payloads
                if 'payload' in message and 'action' in message['payload']:
                    payload = message['payload']
                    action = payload['action']
                    if action == 'show_url':

                        self.tablet.showWebview(payload['url'])

                    elif action == 'show_local':  # TODO: Collapse into show_url...

                        path = payload['path']
                        url = 'http://%s/apps/%s' % (self.tablet.robotIp(),
                                                     os.path.join(self.package_uuid,
                                                                  os.path.normpath(path).lstrip("\\/"))
                                                     .replace(os.path.sep, "/"))

                        self.tablet.showWebview(str(url))

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

    # TODO: Fix the eyes?

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
        self.leds.fadeRGB("FaceLeds", r / 255, g / 255, b / 255, 0)


if __name__ == "__main__":
    stk.runner.run_service(ListenerService)