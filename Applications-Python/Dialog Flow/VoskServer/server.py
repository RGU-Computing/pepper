# Python 3 Server for vosk.
# This is a proof of concept, it ignores socket disconnections and doesn't gracefully exit when pressing ctrl+c (press return instead).

from vosk import Model, KaldiRecognizer, SetLogLevel

import json
import os
import signal
import socket
import struct
import sys
from threading import Thread
import time
import wave

# Init en-us Vosk model.
model = Model(lang="en-us")


class SocketServer(Thread):
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 9090))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")

                    # rec = KaldiRecognizer(model, 44100)  # TODO Don't hard code this.
                    rec = KaldiRecognizer(model, 16000)  # TODO Don't hard code this.
                    rec.SetWords(True)
                    rec.SetPartialWords(True)

                    buf = bytes()
                    while len(buf) < 4:
                        buf += conn.recv(4)
                    response_len = struct.unpack('!i', buf[:4])[0]

                    print(response_len)

                    read_count = 0
                    datbuf = bytes()
                    while read_count < response_len:
                        data = conn.recv(4096)
                        datbuf += data
                        read_count += len(data)

                        # Accepting each chunk like this seems to yield better results
                        rec.AcceptWaveform(data)

                    print('generate response')

                    print('send response')
                    resp = json.loads(rec.FinalResult())['text']
                    print(resp)
                    conn.sendall(struct.pack("!i", len(resp)))
                    conn.sendall(resp.encode('utf8'))

                    # Wait for client to close.
                    # conn.recv(1)
                    time.sleep(1)

                    print('end')


# https://stackoverflow.com/questions/15189888/python-socket-accept-in-the-main-thread-prevents-quitting
pid = os.getpid()
sl = SocketServer()
sl.start()
input('Socket is listening, press any key to abort...')
os.kill(pid, 9)
