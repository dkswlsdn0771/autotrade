from os import access
import time
import pybithumb
import datetime
import requests

key = ""
secret = ""
myToken = "xoxb-4090417448918-4082477571863-PC976IVN2IQbbdnT2TZc6XRg"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

# 로그인
bithumb = pybithumb.Bithumb(key, secret)
print("자동매매를 시작합니다")
# 시작 메세지 슬랙 전송
post_message(myToken,"#trade", "자동매매를 시작합니다!")

#with open("bithumb.txt") as f:
    ##lines = f.readlines()
    #key = lines[0].strip()
    #secret = lines[1].strip()
    #bithumb = pybithumb.Bithumb(key, secret)

def get_target_price(ticker):
    df = pybithumb.get_ohlcv(ticker)
    yesterday = df.iloc[-2]

    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + (yesterday_high - yesterday_low) * 0.5
    return target

def buy_crypto_currency(ticker):
    krw = bithumb.get_balance(ticker)[2]
    orderbook = pybithumb.get_orderbook(ticker)
    sell_price = orderbook['asks'][0]['price']   
    unit = krw/float(sell_price)
    bithumb.buy_market_order(ticker, unit)

def sell_crypto_currency(ticker):
    unit = bithumb.get_balance(ticker)[0]
    bithumb.sell_market_order(ticker, unit)

def get_yesterday_ma5(ticker):
    df = pybithumb.get_ohlcv(ticker)
    close = df['close']
    ma = close.rolling(5).mean()
    return ma[-2]

now = datetime.datetime.now()
mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
ma5 = get_yesterday_ma5("BTC")
target_price = get_target_price("BTC")

while True:
    try:
        now = datetime.datetime.now()
        if mid < now < mid + datetime.delta(seconds=10): 
            target_price = get_target_price("BTC")
            mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
            ma5 = get_yesterday_ma5("BTC")
            sell_crypto_currency("BTC")
            post_message(myToken,"#trade", "BTC을 매도하였습니다")  
    
        current_price = pybithumb.get_current_price("BTC")        
        if (current_price > target_price) and (current_price > ma5):
            buy_crypto_currency("BTC")
            post_message(myToken,"#trade", "BTC을 매수하였습니다")        
    except:
        print("에러 발생")     
        post_message(myToken,"#trade", "에러가 발생하였습니다")   
    time.sleep(1)
