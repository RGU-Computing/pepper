import speech_recognition as sr
import requests
import time

api_url = 'http://127.0.0.1:5000'

def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Pepper-GPT active....")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Error; request failed"

def call_pepper_api(text):
    params = {'user_input': text}
    data = {'user_input': text}
    response = requests.post(api_url, json=data)
    return True

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        text = recognize_speech_from_mic(recognizer, microphone)
        print("Pepper processing:", text)

        if text and text not in ["Could not understand audio", "Error; request failed"]:
            response = call_pepper_api(text)

        time.sleep(1)

if __name__ == "__main__":
    main()
