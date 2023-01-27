from telethon.sync import TelegramClient, events
from binance import Client
import re



report_in_channel = -1001805018828

binance_client = Client(binance_api_key, binance_secret, testnet=True)
order = binance_client.futures_create_order(symbol='BTCUSDT', side='BUY', type='LIMIT', quantity=0.01, timeInForce='GTC', price=25000)
print(order)
exit()

def get_account_balance():
    balance = client.futures_account_balance()[6]['balance']
    return float(balance)

def get_min_quant(symbol):
    info = client.futures_exchange_info()
    for item in info['symbols']:
        if item['symbol'] == symbol:
            for f in item['filters']:
                if f['filterType'] == 'PRICE_FILTER':
                    return f['tickSize']

with TelegramClient('client', telegram_api_id, telegram_api_hash) as client:
    @client.on(events.NewMessage)
    async def new_message_handler(event):
        if event.raw_text.startswith('HQ |HQ'):
            parsed_message = event.raw_text.split("|")
            pair = parsed_message[2].split(' ')[0]
            signal = parsed_message[3].split(' SIGNAL')[0].strip()
            prob = re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[5].split(' :')[1])[0]
            entry = re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[6].split(' @ ')[1])[0]
            tp1 = re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[7].split(' : ')[1])[0]
            tp2 = re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[8].split(' : ')[1])[0]
            stop_loss = re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[9].split(' : ')[1])[0]

            print('PAIR:' + pair)
            print('SIGNAL:' + signal)
            print('PROB:' + prob )
            print('ENTRY:' + entry)
            print('TP1:' + tp1)
            print('TP2:' + tp2)
            print('STOP LOSS:' + stop_loss)
            await client.send_message(report_in_channel, f"{pair} {signal} @{entry} TP1: {tp1} TP2: {tp2} SL: {stop_loss} {prob}%")

    client.run_until_disconnected()
