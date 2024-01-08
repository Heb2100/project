from data import test_KOSDQ, test_KOSPI
from tel import test_chat_id, test_tel_send, tel_send_user
import asyncio

# async def main():
#     await test_chat_id.get_chat_id()

def telegram_send(tmp):
    l = []; tmp_send = []
    for i in range(10):
        try:
            tmp_row = ("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(tmp[i][3], tmp[i][4], tmp[i][5], tmp[i][6], tmp[i][7], tmp[i][8], tmp[i][9], tmp[i][10], tmp[i][11]))
            tmp_send.append(tmp_row)
        except Exception as e:
            l.append('\n')
    tmp = '\n'.join(tmp_send)
    tel_send_user.main(tmp)

telegram_send(test_KOSDQ.KOSDQ())
telegram_send(test_KOSPI.KOSPI())