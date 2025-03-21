# This exposes the basics of the Dialog Flow API to NAOqi through a module.
# Due to NAOqi broker weirdness, the responses are passed back to the caller as a JSON string.
# This has to be loaded into a dict and run through the function in the example listener called "byteify"
# This converts the unicode strings to ASCII and makes them work with the rest of your code and NAOqi.

import dialogflow_v2 as dialogflow
from dialogflow_v2.proto.session_pb2 import QueryInput, TextInput
from dialogflow_v2.proto.audio_config_pb2 import InputAudioConfig, AudioEncoding
from google.protobuf.json_format import MessageToJson
from naoqi import ALBroker, ALModule

import argparse
import sys
import time


def log_response(response):
    """
    Print the dialogflow response to the console for debugging purposes.
    """
    
    print("=" * 20)
    print("Query text: {}".format(response.query_result.query_text))
    print(
        "Detected intent: {} (confidence: {})\n".format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence,
        )
    )
    print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text.encode('utf8')))


class DialogFlowAPI(ALModule):
    """NAOqi remote module that interfaces with Google DialogFlow."""

    def __init__(self, name):
        ALModule.__init__(self, name)

        # Gross imports because of py2
        self.session_client = dialogflow.SessionsClient()
        self.session = None
        self.language_code = "en-GB"
        pass

    def begin_session(self, project_id, session_id, language_code):
        """
        Start the dialog flow session.
        :param project_id: The google project ID, used to find the agent.
        :param session_id: The session ID (for contexts).
        :param language_code: The language being understood.
        :return:
        """
        if self.session is not None:
            print('[DialogFlow] Session already active.')
            return
        self.session = self.session_client.session_path(project_id, session_id)
        self.language_code = language_code
        print("[DialogFlow] Session path: {}\n".format(self.session))

    def end_session(self):
        """
        Clear the session ready for reuse.
        """
        print('[DialogFlow] Ending session.')
        self.session = None

    def detect_intent_text(self, text):
        """Detect intent from the given text string."""

        # Collect input
        text_input = TextInput(text=text, language_code=self.language_code)

        # Build and send query
        query_input = QueryInput(text=text_input)
        response = self.session_client.detect_intent(self.session, query_input)
        log_response(response)

        # Send it as json because naoqi doesnt like objects
        return str(MessageToJson(response))

    def detect_intent_audio(self, input_audio):
        """Detect intent from the given PWM audio"""
        # Hardcoded Pepper's values
        audio_encoding = AudioEncoding.AUDIO_ENCODING_LINEAR_16
        sample_rate_hertz = 16000

        # Build audio config and inputs
        audio_config = InputAudioConfig(
            audio_encoding=audio_encoding,
            language_code=self.language_code,
            sample_rate_hertz=sample_rate_hertz,
        )
        query_input = QueryInput(audio_config=audio_config)

        # Fetch intent.
        response = self.session_client.detect_intent(self.session, query_input, input_audio=input_audio)
        log_response(response)

        # Send it as json because naoqi doesnt like objects
        return str(MessageToJson(response))


if __name__ == '__main__':
    # Nifty way of grabbing terminal arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='Robot IP Address. For local bot use 127.0.0.1.')
    parser.add_argument('--port', type=int, default=9559, help='NaoQI port number.')
    args = parser.parse_args()

    try:
        # Setup a bi-directional broker to communicate with Pepper.
        pythonBroker = ALBroker('pythonBroker', '0.0.0.0', 9999, args.ip, args.port)
    except RuntimeError:
        print('Failed to connect to Naoqi at %s:%d. Please check script arguments. Run with -h for help.' % (
            args.ip, args.port))
        sys.exit(1)

    # Register the module.
    DialogFlowAPI = DialogFlowAPI('DialogFlowAPI')

    # Keep program running until we tell it to quit.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user, stopping application.")
        sys.exit(0)
