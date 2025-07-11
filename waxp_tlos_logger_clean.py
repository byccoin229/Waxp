
import requests
import time
import threading
from flask import Flask, request

TELEGRAM_BOT_TOKEN = '8183...'
TELEGRAM_CHAT_ID = '-1002813651741'
WAX_ACCOUNT = 'bitgetxpr'
CHECK_INTERVAL = 10  # in seconds
last_tx = None

app = Flask(__name__)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=data)
    if not response.ok:
        print("Failed to send message:", response.text)

def get_account_actions(account):
    url = f"https://wax.eosusa.io/v2/history/get_actions?account={account}&limit=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['actions']
    except Exception as e:
        print(f"Error fetching actions: {e}")
        return []

def monitor_deposits():
    global last_tx
    print("Monitoring started...")
    while True:
        actions = get_account_actions(WAX_ACCOUNT)
        if actions:
            act = actions[0]['act']
            tx_id = actions[0]['trx_id']
            if act['name'] == 'transfer' and act['data']['to'] == WAX_ACCOUNT:
                if tx_id != last_tx:
                    last_tx = tx_id
                    from_acc = act['data']['from']
                    quantity = act['data']['quantity']
                    memo = act['data']['memo']
                    message = f"💰 *New Deposit*

From: `{from_acc}`
Amount: `{quantity}`
Memo: `{memo}`"
                    print(message)
                    send_telegram_message(message)
        time.sleep(CHECK_INTERVAL)

@app.route('/', methods=['GET', 'POST'])
def index():
    return 'Bot is running.'

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def receive_update():
    update = request.get_json()
    if 'message' in update and 'text' in update['message']:
        chat_id = update['message']['chat']['id']
        text = update['message']['text']
        if text == '/start':
            send_telegram_message("👋 Bot is active and monitoring deposits.")
    return '', 200

if __name__ == "__main__":
    monitor_deposits()
