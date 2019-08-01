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
key = '<AZURE-COMPUTER-VISION-SUBSCRIPTION-KEY>'
credentials = CognitiveServicesCredentials(key)
client = ComputerVisionClient(endpoint, credentials)

# =========== Setup translator client ============
subscriptionKey = '<AZURE-TRANSLATE-SUBSCRIPTION-KEY>'
base_url = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
languages = {'de':'german', 'it':'italian', 'en':'english', 'ms':'malay', 'pt':'portuguese','es':'spanish', 'id':'indonesian'}
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
    elif 'voice' in results[latest_update]['message'].keys(): 
        file_id = results[latest_update]['message']['voice']["file_id"]
        file_info = requests.get(bot + 'getFile', params={"chat_id": chat_id, "file_id": file_id})
        file_path = file_info.json()['result']['file_path']
        data = file_url + file_path
        data_type = 'audio'
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
        sentence = sentence + line.text + '\n'
    return sentence

def translate(url, text):
    body = [{'text': text}]
    request = requests.post(url, headers=headers, json=body)
    if request.json()[0]['detectedLanguage']['language'] in languages.keys():
        from_lang = str(languages[request.json()[0]['detectedLanguage']['language']])
    else:
        from_lang = 'unknown'
    if request.json()[0]['translations'][0]['to'] in languages.keys():
        to_lang = str(languages[request.json()[0]['translations'][0]['to']])
    else:
        to_lang = 'unknown'
    if len(str(request.json()[0]['translations'][0]['text']))>1:
        translated_text = str(request.json()[0]['translations'][0]['text'])
    else:
        translated_text: 'UNABLE TO TRANSLATE'
    translated = 'Translated from ' + from_lang + ' to '+ to_lang + ':\n' + translated_text 
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
            elif message_type == 'audio':
                reply = 'Invalid input. Please send an image'
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
                elif message == '/german':
                    translate_url = base_url + '&to=de'
                    reply = 'Language set to German'
                    send_message(chat_id, reply)
                elif message == '/italian':
                    translate_url = base_url + '&to=it'
                    reply = 'Language set to Italian'
                    send_message(chat_id, reply)
                elif message == '/malay':
                    translate_url = base_url + '&to=ms'
                    reply = 'Language set to Malay'
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


        