from flask import Flask, request, Response
import requests
import schedule
import time
import finnhub
from multiprocessing import Process
import sys


def check_stock_price(ticker, desired_price, username):
    finnhub_client = finnhub.Client(api_key="")
    quote = finnhub_client.quote(ticker)
    print("Desired Price", desired_price, "Quote:", quote["c"])
    if str(desired_price) == str(quote["c"]):
        print("Hello")
        x = requests.post(url, data={"Ticker": ticker, "User": username, "Price": desired_price})
        print(x.text, x.status_code)
        return schedule.CancelJob


# url of main implementation file
url = "http://226e-2001-1970-51a4-fd00-00-7213.ngrok.io/trigger_price_alert"


ticker = sys.argv[1]
user = sys.argv[3]
price = sys.argv[2]

schedule.every(4).seconds.do(lambda: check_stock_price(ticker, price, user))

while True:
    schedule.run_pending()
    time.sleep(1)



