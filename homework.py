import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PROXY_URL = os.getenv('PROXY_URL')
API_HOMEWORK_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
PROXY = telegram.utils.request.Request(
    proxy_url=PROXY_URL)
BOT = telegram.Bot(token=TELEGRAM_TOKEN, request=PROXY)


def parse_homework_status(homework):
    if homework.get("homework_name") is None:
        raise KeyError('В ответе отсутствует ключ "homework_name"')
    homework_name = homework["homework_name"]
    if homework.get("status") is None:
        raise KeyError('В ответе отсутствует ключ "status"')
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {
        'from_date': current_timestamp
    }
    homework_statuses = requests.get(
        API_HOMEWORK_URL, headers=headers, params=params)
    try:
        return homework_statuses.json()
    except ValueError:
        return {}
        print('Невалидный JSON')


def send_message(message):
    return BOT.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get(
                'current_date')  # обновить timestamp
            time.sleep(10 * 60)  # опрашивать раз в 10 минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()