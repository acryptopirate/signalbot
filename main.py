from telethon.sync import TelegramClient, events
from binance import Client
import re
import time
from datetime import datetime

telegram_api_id = 28774191
telegram_api_hash = '6d2a0150de7fc0b054986c844b24c34a'

binance_api_key = '2090fb1c85b1aae449518e990abd9aee913ac12f81ed1a665a6d02106b66f99d'
binance_secret = 'f617383d6ee61536effee19e8f4d129cda5a0e0aafaccbb37aa9f36935dc2b08'

report_in_channel = -1001805018828

min_probability = 49

pairs = {
    # 'ALGUSD': 'ALGOUSDT',
    # 'AVAUSD': 'AVAXUSDT',
    # 'AXSUSD': 'AXSUSDT',
    # 'ADAUSD': 'ADAUSDT',
    # 'BCHUSD': 'BCHUSDT',
    # 'BATUSD': 'BATUSDT',
    # 'DSHUSD': 'DASHUSDT',
    # 'DOTUSD': 'DOTUSDT',
    # 'LTCUSD': 'LTCUSDT',
    # 'LRCUSD': 'LRCUSDT',
    # 'LNKUSD': 'LINKUSDT',
    # 'MKRUSD': 'MKRUSDT',
    # 'MTCUSD': 'MATICUSDT',
    # 'ETHUSD': 'ETHUSDT',
    # 'ETCUSD': 'ETCUSDT',
    # 'SOLUSD': 'SOLUSDT',
    # 'INCUSD': '1INCHUSDT',
    # 'NEOUSD': 'NEOUSDT',
    # 'NERUSD': 'NEARUSDT',
    # 'SANUSD': 'SANDUSDT',
    # 'IOTUSD': 'IOTAUSDT',
    # 'UNIUSD': 'UNIUSDT',
    # 'CRVUSD': 'CRVUSDT',
    # 'FILLUSD': 'FILLUSDT',
    # 'FTMUSD': 'FTMUSDT',
    # 'XMRUSD': 'XMRUSDT',
    # 'XTZUSD': 'XTZUSDT',
    # 'VECUSD': 'VETUSDT',
    # 'TRXUSD': 'TRXUSDT',
    # 'OMGUSD': 'OMGUSDT',
    # 'ZECUSD': 'ZECUSDT',
    # 'RLCUSD': 'RLCUSDT',
    # 'BNBUSD': 'BNBUSDT',
    # 'XRPUSD': 'XRPUSDT',
    # 'DOGUSD': 'DOGEUSDT',
    # 'ATMUSD': 'ATOMUSDT',
    # 'ONEUSD': 'ONEUSDT',
    # 'SUSUSD': 'SUSHIUSDT',
    'BTCUSDT': 'BTCUSDT',
    'ETHUSDT': 'ETHUSDT'
}

bet_usdt = 500
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
        if event.raw_text.startswith('BTCUSDT MARKET ') or event.raw_text.startswith('ETHUSDT MARKET '):
            symbol = ''
            message = ''
            acc_balance = (binance_client.futures_account_balance())
            for symbol_balance in acc_balance:
                if symbol_balance['asset'] == 'USDT':
                    balance_string = symbol_balance['balance']
            print('BALANCE')
            print(balance_string)
            parsed_message = event.raw_text.split(" ")
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            print(parsed_message)

            pair = parsed_message[0]
            signal = parsed_message[2]
            entry = parsed_message[3]
            tp1 = float(parsed_message[5])
            tp2 = float(parsed_message[7])
            stop_loss = float(parsed_message[9])

            opposite_side = ''
            errors = []
            success = []
            print(f"{symbol} {signal} TP1: {tp1} SL: {stop_loss} \n")
            if (signal == 'BUY'):
                opposite_side = 'SELL'
            elif(signal == 'SELL'):
                opposite_side = 'BUY'

            if pair not in pairs:
                if pair not in pairs:
                    errors.append('Unknown pair')
                symbol = pair
            else:
                symbol = pairs[pair]

                print('Set leverage')
                binance_client.futures_change_leverage(leverage=100, symbol=symbol)
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
                        quantity=quantity,
                        reduceOnly=False,
                        positionSide='BOTH'
                    )
                    success.append('POSITION')

                    print('Create Tp1')
                    sell_gain_market_long = binance_client.futures_create_order(
                        symbol=symbol,
                        side=opposite_side,
                        type='TAKE_PROFIT_MARKET',
                        quantity=quantity,
                        stopPrice=round(tp1, get_price_precision(symbol=symbol)),
                        closePosition=True,
                        timeInForce='GTE_GTC', workingType='MARK_PRICE',
                        placeType='position'
                    )
                    success.append('TP1')

                    # print('Create Tp1')
                    # sell_gain_market_long = binance_client.futures_create_order(
                    #     symbol=symbol,
                    #     side=opposite_side,
                    #     type='TAKE_PROFIT_MARKET',
                    #     quantity=round(quantity / 2, get_quantity_precision(symbol=symbol)),
                    #     stopPrice=round(tp1, get_price_precision(symbol=symbol))
                    # )
                    # success.append('TP1')

                    print('Create SL')
                    sell_stop_market_short = binance_client.futures_create_order(
                        symbol=symbol,
                        side=opposite_side,
                        type='STOP_MARKET',
                        quantity=quantity,
                        stopPrice=round(stop_loss, get_price_precision(symbol=symbol)),
                        timeInForce='GTE_GTC', reduceOnly=True, workingType='MARK_PRICE',
                        placeType='position'
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
            message = message + f"BALANCE {round(float(balance_string),2)}$ \n"
            message = message + f"{symbol} {signal} TP1: {tp1} SL: {stop_loss} \n"
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
