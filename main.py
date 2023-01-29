from telethon.sync import TelegramClient, events
from binance import Client
import re
import time
from datetime import datetime

telegram_api_id = 28774191
telegram_api_hash = '6d2a0150de7fc0b054986c844b24c34a'

binance_api_key = '177a9229ae61848d388b9913b518540d30cfea19e245fdfc2a66dba13d844eea'
binance_secret = '013059725d5a9fba39b12ae5d69082c8eded15d983ccec647e87e6ad0fc0f563'

report_in_channel = -1001805018828

min_probability = 69

pairs = {
    'ALGUSD': 'ALGOUSDT',
    'AVAUSD': 'AVAXUSDT',
    'AXSUSD': 'AXSUSDT',
    'ADAUSD': 'ADAUSDT',
    'BCHUSD': 'BCHUSDT',
    'BATUSD': 'BATUSDT',
    'DSHUSD': 'DASHUSDT',
    'DOTUSD': 'DOTUSDT',
    'LTCUSD': 'LTCUSDT',
    'LRCUSD': 'LRCUSDT',
    'LNKUSD': 'LINKUSDT',
    'MKRUSD': 'MKRUSDT',
    'MTCUSD': 'MATICUSDT',
    'ETHUSD': 'ETHUSDT',
    'ETCUSD': 'ETCUSDT',
    'SOLUSD': 'SOLUSDT',
    'INCUSD': '1INCHUSDT',
    'NEOUSD': 'NEOUSDT',
    'NERUSD': 'NEARUSDT',
    'SANUSD': 'SANDUSDT',
    'IOTUSD': 'IOTAUSDT',
    'UNIUSD': 'UNIUSDT',
    'CRVUSD': 'CRVUSDT',
    'FILLUSD': 'FILLUSDT',
    'FTMUSD': 'FTMUSDT',
    'XMRUSD': 'XMRUSDT',
    'XTZUSD': 'XTZUSDT',
    'VECUSD': 'VETUSDT',
    'TRXUSD': 'TRXUSDT',
    'OMGUSD': 'OMGUSDT',
    'ZECUSD': 'ZECUSDT',
    'RLCUSD': 'RLCUSDT',
    'BNBUSD': 'BNBUSDT',
    'XRPUSD': 'XRPUSDT',
    'DOGUSD': 'DOGEUSDT',
    'ATMUSD': 'ATOMUSDT',
    'ONEUSD': 'ONEUSDT',
    'SUSUSD': 'SUSHIUSDT',
    'BTCUSD': 'BTCUSDT'
}

bet_usdt = 200
quantity = 0.01
binance_client = Client(binance_api_key, binance_secret, testnet=True)
exchange_info = binance_client.futures_exchange_info()


def get_quantity_precision(symbol):
   for x in exchange_info['symbols']:
    if x['symbol'] == symbol:
        return x['quantityPrecision']


def get_price_precision(symbol):
    for x in exchange_info['symbols']:
        if x['symbol'] == symbol:
            return x['pricePrecision']

def get_usdt_balance():
    balance = binance_client.futures_account_balance()
    for check_balance in balance:
        if check_balance["asset"] == "USDT":
            usdt_balance = check_balance["balance"]

    return usdt_balance


def get_min_quant(symbol):
    info = binance_client.futures_exchange_info()
    for item in info['symbols']:
        if item['symbol'] == symbol:
            for f in item['filters']:
                if f['filterType'] == 'PRICE_FILTER':
                    return f['tickSize']


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
        if event.raw_text.startswith('HQ ') or event.raw_text.startswith('SYND TOP/BOTTOM'):
            symbol = ''
            message = ''
            parsed_message = event.raw_text.split("|||")
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            print(parsed_message)
            if event.raw_text.startswith('HQ '):
                pair = parsed_message[2].split(' ')[0]
                signal = parsed_message[3].split(' SIGNAL')[0].strip()
                prob = float(re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[5].split(' :')[1])[0])
                entry = re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[6].split(' @ ')[1])[0]
                tp1 = float(re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[7].split(' : ')[1])[0])
                tp2 = float(re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[8].split(' : ')[1])[0])
                stop_loss = float(re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[9].split(' : ')[1])[0])
            else:
                pair = parsed_message[1].split(' ')[0]
                signal = 'BUY'
                prob = 101
                entry = re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[2].split(' @')[1])[0]
                tp1 = float(re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[3].split('TP1 :')[1])[0])
                tp2 = float(re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[4].split('TP2 :')[1])[0])
                stop_loss = float(re.findall(r"[-+]?\d*\.\d+|\d+", parsed_message[5].split('SL :')[1])[0])
            opposite_side = ''
            errors = []
            success = []
            if (signal == 'BUY'):
                opposite_side = 'SELL'
            elif(signal == 'SELL'):
                opposite_side = 'BUY'

            if pair not in pairs or prob < min_probability:
                if pair not in pairs:
                    errors.append('Unknown pair')
                if prob < min_probability:
                    errors.append('Low probability ')
                symbol = pair
            else:
                symbol = pairs[pair]

                print('Set leverage')
                binance_client.futures_change_leverage(leverage=20, symbol=symbol)
                print('Cancel old orders for pair ' + symbol)
                binance_client.futures_cancel_all_open_orders(symbol=symbol, timestamp=time.time())
                positions = binance_client.futures_account()['positions']
                print('Get current price')
                price = float(binance_client.futures_symbol_ticker(symbol=symbol)['price'])
                quantity = round(bet_usdt / price, get_quantity_precision(symbol=symbol))

                if pair in pairs:
                    for position in positions:
                        if position['symbol'] == symbol:
                            old_position = position

            if not len(errors):
                try:
                    print('Create Position ' + signal + ' : ' + str(quantity))
                    position = binance_client.futures_create_order(
                        symbol=symbol,
                        side=signal,
                        type='MARKET',
                        quantity=quantity
                    )
                    success.append('POSITION')

                    print('Create Tp2')
                    sell_gain_market_long = binance_client.futures_create_order(
                        symbol=symbol,
                        side=opposite_side,
                        type='TAKE_PROFIT_MARKET',
                        quantity=quantity,
                        closePosition=True,
                        stopPrice=round(tp2, get_price_precision(symbol=symbol))
                    )
                    success.append('TP2')

                    print('Create Tp1')
                    sell_gain_market_long = binance_client.futures_create_order(
                        symbol=symbol,
                        side=opposite_side,
                        type='TAKE_PROFIT_MARKET',
                        quantity=round(quantity / 2, get_quantity_precision(symbol=symbol)),
                        stopPrice=round(tp1, get_price_precision(symbol=symbol))
                    )
                    success.append('TP1')

                    print('Crate SL')
                    sell_stop_market_short = binance_client.futures_create_order(
                        symbol=symbol,
                        side=opposite_side,
                        type='STOP_MARKET',
                        quantity=quantity,
                        stopPrice=round(stop_loss, get_price_precision(symbol=symbol))
                    )
                    success.append('SL')
                except Exception as exs:
                    errors.append(str(exs))
                    print('Exception ' + str(exs))
                    print('Cancel all open orders')
                    binance_client.futures_cancel_all_open_orders(symbol=symbol, timestamp=time.time())
                    if 'POSITION' in success:
                        print('Revert position')
                        binance_client.futures_create_order(symbol=symbol, type="MARKET", side=opposite_side, quantity=quantity)

            message = message + f"NEW SIGNAL \n"
            message = message + f"{symbol} {signal} TP1: {tp1} TP2: {tp2} SL: {stop_loss} {prob}% \n"
            if len(errors):
                for error in errors:
                    message = message + 'ERROR\n' + str(error)
            elif len(success):
                message = message + 'DONE\n'

            await client.send_message(report_in_channel, message)

            errors.clear()
            message = ''
            success.clear()

    client.run_until_disconnected()
