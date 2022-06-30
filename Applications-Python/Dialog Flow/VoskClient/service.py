# This is a prototype helper for using Vosk from Python 2
# It could be cleaner to write a Vosk Module in C++, however it was done like this for prototyping sakes.

from naoqi import ALModule

import socket
import struct


class VoskClient(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)

    # Streaming may work better than dumping.
    def transcribe(self, audio):
        try:
            # Connect to the server/
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', 9090))

            # Send the audio
            s.sendall(struct.pack('!i', len(audio)))
            s.sendall(audio)

            # Read response length
            buf = bytes()
            while len(buf) < 4:
                buf += s.recv(4)
            response_len = struct.unpack('!i', buf[:4])[0]

            print(response_len)

            # Read response
            response = bytes()
            while len(response) < response_len:
                response += s.recv(response_len - len(response))
                print(len(response))

            resp = response.decode('utf8')
            s.close()
            return str(resp)
        except Exception as ex:
                print('=' * 20)
                print('Ex: %s' % ex.message)


if __name__ == '__main__':
    # Nifty way of grabbing terminal arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default='127.0.0.1', help='Robot IP Address. For local bot use 127.0.0.1.')
    parser.add_argument('--port', type=int, default=9559, help='NaoQI port number.')
    parser.add_argument('--project_id', type=str, required=True, help='Google Cloud Project ID.')
    args = parser.parse_args()

    try:
        # Setup a bi-directional broker to communicate with Pepper.
        pythonBroker = ALBroker('pythonBroker', '0.0.0.0', 9999, args.ip, args.port)
    except RuntimeError:
        print('Failed to connect to Naoqi at %s:%d. Please check script arguments. Run with -h for help.' % (
            args.ip, args.port))
        sys.exit(1)

    # Register the module.
    VoskClient = VoskClient('VoskClient')

    # Keep program running until we tell it to quit.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user, stopping application.")
        sys.exit(0)

