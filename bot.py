from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
import time
import requests
import uuid

# =========== Setup bot ============
TOKEN = '<BOT-TOKEN>'
bot = "https://api.telegram.org/bot"+TOKEN+"/"
file_url = 'https://api.telegram.org/file/bot'+TOKEN+'/'

# =========== Setup CV client ============
endpoint = '<AZURE-COMPUTER-VISION-ENDPOINT>'
key = '<AZURE-COMPUTER-VISION-SUBSSCRIPTION-KEY>'
credentials = CognitiveServicesCredentials(key)
client = ComputerVisionClient(endpoint, credentials)

# =========== Setup translator client ============
subscriptionKey = '<AZURE-TRANSLATE-SUBSSCRIPTION-KEY>'
base_url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
languages = {'en':'english', 'pt':'portuguese','es':'spanish'}
headers = {
    'Ocp-Apim-Subscription-Key': subscriptionKey,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

def get_message():
    response = requests.get(bot + 'getUpdates', data={'timeout': 100, 'offset': None})
    results = response.json()['result']
    latest_update = len(results) - 1
    chat_id =  results[latest_update]['message']['chat']['id']
    update = results[latest_update]['update_id']
    if 'photo' in results[latest_update]['message'].keys():
        index = len(results[latest_update]['message']['photo']) - 1 
        file_id = results[latest_update]['message']['photo'][index]["file_id"]
        file_info = requests.get(bot + 'getFile', params={"chat_id": chat_id, "file_id": file_id})
        file_path = file_info.json()['result']['file_path']
        data = file_url + file_path
        data_type = 'image'
    else: 
        data = results[latest_update]['message']['text']
        data_type = 'text'
    return chat_id, data, update, data_type

def recognize(photo_url):
    job = client.recognize_text(url=photo_url,mode="Printed",raw=True)
    operation_id = job.headers['Operation-Location'].split('/')[-1]
    image_analysis = client.get_text_operation_result(operation_id)
    while image_analysis.status in ['NotStarted', 'Running']:
        time.sleep(1)
        image_analysis = client.get_text_operation_result(operation_id)
    sentence = ''
    for line in image_analysis.recognition_result.lines:
        sentence = sentence + ' ' + line.text
    return sentence

def translate(url, text):
    body = [{'text': text}]
    request = requests.post(url, headers=headers, json=body)
    translated = 'Translated from ' + str(languages[request.json()[0]['detectedLanguage']['language']]) + ' to ' + str(languages[request.json()[0]['translations'][0]['to']]) + ':\n' + str(request.json()[0]['translations'][0]['text'])
    return translated

def send_message(chat, reply_text):
    params = {'chat_id': chat, 'text': reply_text}
    response = requests.post(bot + 'sendMessage', data=params)
    return response

def main():
    last_update_id = 0
    translate_url = base_url + '&to=en'
    while True:
        chat_id, message, update_id, message_type = get_message()
        if update_id > last_update_id:
            if message_type == 'image':
                recognized_text = recognize(message)
                if len(recognized_text) > 1:
                    reply = translate(translate_url, recognized_text)
                    send_message(chat_id, reply)
                else:
                    reply = 'Error! Plese use other image'
                    send_message(chat_id, reply)

            else:
                if message == '/start':
                    reply = 'Hi! I am Visual Translator Bot.\nSend a picture to start translation.'
                    send_message(chat_id, reply)
                elif message == '/english':
                    translate_url = base_url + '&to=en'
                    reply = 'Language set to English'
                    send_message(chat_id, reply)
                elif message == '/spanish':
                    translate_url = base_url + '&to=es'
                    reply = 'Language set to Spanish'
                    send_message(chat_id, reply)
                elif message == '/portuguese':
                    translate_url = base_url + '&to=pt'
                    reply = 'Language set to Portuguese'
                    send_message(chat_id, reply)
                elif message == '/help':
                    reply = 'Send an image to start translation or send  /english , /spanish or /portuguese to set the desired translated language.'
                    send_message(chat_id, reply)
                else:
                    reply = 'Invalid input. Please send an image'
                    send_message(chat_id, reply)
            last_update_id = update_id
        else:
            continue

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()