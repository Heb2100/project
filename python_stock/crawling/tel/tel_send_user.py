import argparse
import requests

BOT_TOKEN = "6377969316:AAEKc2q_6u60iFM3idaw0VEihIeC9vXKpTY"
#https://api.telegram.org/bot6377969316:AAEKc2q_6u60iFM3idaw0VEihIeC9vXKpTY/getUpdates

#deploy
CHAT_ID = "-1002018876699"
#for test yeon_bot
# CHAT_ID = "6428201179"

def send_message(message):
    response = requests.post(
        'https://api.telegram.org/bot%s/%s' % (BOT_TOKEN, 'sendMessage'),
        data={
            "chat_id": CHAT_ID,
            "text": message,
        }
    )
    if response.status_code > 200:
        print("Error:", response.text)
def main(str):
    send_message(str)
if __name__ == "__main__":
    main('hi')