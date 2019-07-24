# AzureTranslator
Telegram Bot that can translate text on image using Azure cognitive services API.

## Setup
1. This project require you to have python 3.x, Telegram account and Azure account with active subscription to cognitive service
2. Download the repository or use Git to clone it :
```
git clone https://github.com/haizadtarik/AzureTranslator
```
3. Install dependencies
```
pip install -r requiremnets
```
4. Insert Telegram bot TOKEN, Azure Computer Vision API subscription key and endpoint and Translate Text API subscription key in bot.py
```
# =========== Setup bot ============
TOKEN = '<BOT-TOKEN>'

# =========== Setup CV client ============
endpoint = '<AZURE-COMPUTER-VISION-ENDPOINT>'
key = '<AZURE-COMPUTER-VISION-SUBSSCRIPTION-KEY>'

# =========== Setup translator client ============
subscriptionKey = '<AZURE-TRANSLATE-SUBSSCRIPTION-KEY>'
```
5. Run the code and the Bot can now be used in Telegram.

## Resources
1. [Telegram Bot](https://core.telegram.org/bots)
2. [Azure Cognitive Services](https://docs.microsoft.com/en-us/azure/cognitive-services/)
