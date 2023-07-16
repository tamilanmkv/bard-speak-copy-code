import subprocess
import requests
import json
import sys
from bardapi import Bard
from gtts import gTTS
from playsound import playsound
import re
import dotenv
import clipboard

TOKEN = dotenv.get_key('.env', 'TOKEN') 
if TOKEN == None:
    TOKEN = input("Enter your token: ") 
    with open('.env', 'w') as f:
        f.write(f'TOKEN={TOKEN}')

def detect_device():    
    json_data_audio_devices = subprocess.Popen('system_profiler SPAudioDataType -json', shell=True, stdout=subprocess.PIPE).stdout.read()
    audio_devices = json.loads(json_data_audio_devices)
    for audio_device in audio_devices['SPAudioDataType'][0]['_items']:
        if audio_device['_name'] == "External Microphone":
            return True
    return False

def remove_code_blocks(text):
    # Use regular expression to find and remove code blocks enclosed in ```
    return re.sub(r"```[\s\S]+?```", "", text)

def speak(text):
    # remove between quotes if you want to use google tts
    text = remove_code_blocks(text).replace('**', '')
    tts = gTTS(text=text, lang='en')
    tts.save("tmp.mp3")
    playsound("tmp.mp3")
    subprocess.Popen('rm tmp.mp3', shell=True, stdout=subprocess.PIPE).stdout.read()

def bard_clipboard(text):
    code = re.findall(r"```[\s\S]+?```", text) 
    if len(code) > 0:
        clipboard.copy(code[0].replace('```', ''))

def bard_console(input,session):
    bard = Bard(token=TOKEN,session=session)
    ans= bard.get_answer(input)['content']
    bard_clipboard(ans)
    return ans

def main():
    session = requests.Session()
    session.headers = {
                "Host": "bard.google.com",
                "X-Same-Domain": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Origin": "https://bard.google.com",
                "Referer": "https://bard.google.com/",
                }
    session.cookies.set("__Secure-1PSID", TOKEN) 
    print("Welcome to Bard Console")
    while True:
        input_val = sys.stdin.readline().strip()
        if sys.stdin.isatty():
            if input_val == "exit":
                break
        output = bard_console(input_val,session)
        
        if output != None:
            print(output)
        if detect_device():
            speak(output)

if __name__ == "__main__":
   main() 
