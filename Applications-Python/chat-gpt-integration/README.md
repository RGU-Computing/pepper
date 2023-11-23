# Pepper integration with ChatGPT

This is an example to connect Pepper with ChatGPT via a laptop device. Two applications are used for this setup. One deals with the pepper interface while the other converts speech-to-text. Both runs on a laptop. We opted to use a wireless mic to obtain high quality audio input as pepper's audio in-stream was not effective enough. 

Our Robot runs naoqi version 2.5.5. This is compatible with Python 2.7.9. Other Python versions might have compatibility issues.

The speech recognition server runs on Python 3.10. This was to easily support the speech recognition library.

## Installation

1. Install Python pepper SDK with version 2.5.5 on the laptop and add the system PATH to it. This can be downloaded from https://www.aldebaran.com/en/support/pepper-naoqi-2-9/downloads-softwares.
2. Navigate to 'naoqi-server' path and install requirements with Python 2.7.9.
3. Navigate to 'naoqi-server' path and install requirements with Python 3.10.

## Running

1. Turn Pepper 'on' and connect to the network of the laptop.
2. Configurations must be done on input-gpt-naoqi-server.py to include the Robot IP address and port. This can be run with the Choregraphe simulation as well. We recommend using version 2.5.10.7.
3. Navigate to 'naoqi-server' path and run the below with Python 2.7.9.
```cmd
python input-gpt-naoqi-server
```
4. Navigate to 'speech-recognition-client' path and run the below with Python 3.10.
```cmd
python client
```

