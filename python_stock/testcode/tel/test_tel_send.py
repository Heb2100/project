
import argparse
import requests
# from data import test_KOSDQ
BOT_TOKEN = "6377969316:AAEKc2q_6u60iFM3idaw0VEihIeC9vXKpTY"
CHAT_ID = "6428201179"
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
        # parser = argparse.ArgumentParser("Send messages to my phone")
        # parser.add_argument("messages", nargs="+")
        # args = parser.parse_args()
        # for message in args.messages:
        #     print('message', message)
        #     send_message(message)
if __name__ == "__main__":
#    message = '''
#    Line 1
#Line 2
#Line 3
#    '''
    l = ['1', '2', '3']
    message = '\n'.join(l)
    main(message)