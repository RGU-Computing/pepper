import BaseHTTPServer
import json
import requests
from naoqi import ALBroker, ALModule, ALProxy

# Constants
ROBOT_IP = '127.0.0.1' # This is for the simulation robot in Choreographe. Replace with the actual IP for link.
ROBOT_PORT = 9559 
NAOQI_PORT = 9999
API_KEY = "XXX" # chat-gpt API key
URL = "https://api.openai.com/v1/chat/completions" # chat-gpt API
GPT_MODEL_NAME = "gpt-3.5-turbo-1106" # chat-gpt model

class SpeechModule(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)
        self.tts = ALProxy("ALTextToSpeech")

    def say_text(self, text):
        animated_text = "\\rspd=80\\" + text
        self.tts.say(animated_text)

class ServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        user_input = json.loads(post_data).get('user_input', '')

        try:
            if user_input:
                data = {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input + ". (Limit words to 30)."
                        }
                    ],
                    "model": GPT_MODEL_NAME,
                }
                data["max_tokens"] = 31
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + API_KEY,
                }

                response = requests.post(URL, headers=headers, data=json.dumps(data))
                response.raise_for_status()
                result = response.json()
                answer = result['choices'][0]['message']['content']
                speech_module.say_text(answer.encode('utf-8'))
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"response": answer}))
                return
        except requests.RequestException as e:
            print(e)
            self.send_error(500, "Sorry! Could you repeat please?")
            return
        except Exception as e:
            self.send_error(500, str(e))
            return

def get_naoqi_broker(ip, port):
    try:
        return ALBroker('pythonBroker', '0.0.0.0', NAOQI_PORT, ip, port)
    except RuntimeError:
        raise RuntimeError('Failed to connect to Naoqi at %s:%d. Please check script arguments.')

if __name__ == '__main__':
    python_broker = get_naoqi_broker(ROBOT_IP, ROBOT_PORT)
    speech_module = SpeechModule("speech_module")
    server_address = ('', 5000)
    httpd = BaseHTTPServer.HTTPServer(server_address, ServerHandler)
    print("Starting Naoqi server on port 5000...")
    httpd.serve_forever()
    python_broker.shutdown()
