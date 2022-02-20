from flask import Flask, request, Response
from twilio.twiml.messaging_response import Message, MessagingResponse
import json
from google.cloud import dialogflow
import os
from google.api_core.exceptions import InvalidArgument
import requests
import finnhub
from twilio.rest import Client
import subprocess


# Create separate flask app to do polling
# once notification has been reached, send request back to main file
# open on different ports


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "zoomerJSONFile.json"

## FLAG ----------------------------------------------------

DIALOGFLOW_LANGUAGE_CODE = 'en'


finnhub_client = finnhub.Client(api_key="")
client = Client(ACCOUNT_SID, AUTH_TOKEN)

with open('user_db.json', 'r') as db:
    try:
        users = json.load(db)
    except:
        users = {}


app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def return_sms():

    number = request.form["From"]
    message_body = request.form["Body"]

    response = MessagingResponse()

    # If using a new number
    if number not in users.values():
        response.message(body=f"Hi there! I don't recognize this number. What would you like me to call you?")
        users[f"temp_{str(number)}"] = str(number)
        print(users)
        with open('user_db.json', 'w') as db:
            json.dump(users, db)

        return Response(str(response), mimetype="text/xml")

    # Register new number under a name
    else:
        fulfillment_text, intent = detect_intent_texts(f"{number}", message_body, 'en')
        print("Intent: ", intent)

        if str(intent) == "Welcome":
            response.message(str(fulfillment_text))

        elif str(intent) == "New_User":
            response.message(body=f"Hey there {str(fulfillment_text)}! I will remember your name from here on out! "
                                  f"It is very nice to meet you! I'm here to help make investing in the stock market easier, simpler, and more convenient!"
                                  f" Please let me know what I can do for you!")

            users[fulfillment_text] = users.pop(f"temp_{str(number)}")
            with open('user_db.json', 'w') as db:
                json.dump(users, db)

        elif str(intent) == "Get Stock Price":
            username = get_user(str(number))
            print(fulfillment_text)
            quote = finnhub_client.quote(f"{fulfillment_text}")

            print(quote)
            current_price = quote["c"]
            open_price = quote["o"]
            high_price = quote["h"]

            response.message(f"No problem {username}! The current price for {fulfillment_text} is {current_price}. {fulfillment_text} opened this morning "
                             f"at {open_price} and reached a high of {high_price} today! ")

        elif str(intent) == "Schedule_Notification":
            username = get_user(str(number))
            ticker = str(fulfillment_text).split()[0]
            price = str(fulfillment_text).split()[1]
            #requests.post("http://127.0.0.1:5050/start-polling", data={"Ticker": ticker, "User": username, "Price": price})
            subprocess.Popen(f"bash polling.sh -c {ticker} -e {price} -r {username}")
            print("Ticker: ", ticker, "Price: ", price, "User: ", username)
            #response.message(f"Notification request sent. Status code: {x.status_code}, {x.text}")
            response.message("Got it! Notification has been set! We will notify you if your price point has been reached!")

        elif str(intent) == "30D_High":
            username = get_user(str(number))
            alpha_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={fulfillment_text}&apikey=8QQ2QBV3XE6I0PDB'
            r = requests.get(alpha_url)
            data = r.json()
            latest_refresh = data["Meta Data"]["3. Last Refreshed"]
            m_High = data["Monthly Time Series"][str(latest_refresh)]["2. high"]
            response.message(f"Wow would you look at that 30D High! \n ${m_High}")


        elif str(intent) == "30D_Low":
            username = get_user(str(number))
            alpha_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={fulfillment_text}&apikey=8QQ2QBV3XE6I0PDB'
            r = requests.get(alpha_url)
            data = r.json()
            latest_refresh = data["Meta Data"]["3. Last Refreshed"]
            m_Low = data["Monthly Time Series"][str(latest_refresh)]["2. high"]
            response.message(f"Wow would you look at that 30D Low! \n ${m_Low}")


        elif str(intent) == "7D_High":
            username = get_user(str(number))
            alpha_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={fulfillment_text}&apikey=8QQ2QBV3XE6I0PDB'
            r = requests.get(alpha_url)
            data = r.json()
            latest_refresh = data["Meta Data"]["3. Last Refreshed"]
            #print(data)
            w_High = data["Weekly Time Series"][str(latest_refresh)]["2. high"]
            response.message(f"Wow would you look at that 7D High! \n ${w_High}")

        elif str(intent) == "7D_Low":
            username = get_user(str(number))
            alpha_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={fulfillment_text}&apikey=8QQ2QBV3XE6I0PDB'
            r = requests.get(alpha_url)
            data = r.json()
            latest_refresh = data["Meta Data"]["3. Last Refreshed"]
            # print(data)
            w_Low = data["Weekly Time Series"][str(latest_refresh)]["3. low"]
            response.message(f"Wow would you look at that 7D Low! \n ${w_Low}")

        elif str(intent) == "Stock_Info":
            username = get_user(str(number))
            results = finnhub_client.company_profile2(symbol=str(fulfillment_text))
            message = client.messages.create(
                body=f'Ok here is what I found:',
                from_="+19126168686",
                to=f"{users[username]}"
            )

            response.message(str(results))

        elif str(intent) == "Investopedia_Info":
            username = get_user(str(number))
            print(str(fulfillment_text))
            if str(fulfillment_text) == "stocks":
                message = client.messages.create(
                    body=f'Ok here is what I found. This article will help explain stocks a bit more!',
                    from_="+19126168686",
                    to=f"{users[username]}"
                )

                response.message("https://www.investopedia.com/stocks-4427785")

            elif str(fulfillment_text) == "Mutual_Funds":
                username = get_user(str(number))
                message = client.messages.create(
                    body=f'Ok here is what I found. This article will help explain mutual funds a bit more!',
                    from_="+19126168686",
                    to=f"{users[username]}"
                )

                response.message("https://www.investopedia.com/mutual-funds-4427787")

            elif str(fulfillment_text) == "ETF":
                username = get_user(str(number))
                message = client.messages.create(
                    body=f'Ok here is what I found. This article will help explain ETF a bit more!',
                    from_="+19126168686",
                    to=f"{users[username]}"
                )

                response.message("https://www.investopedia.com/terms/e/etf.asp")

            elif str(fulfillment_text) == "401k":
                username = get_user(str(number))
                message = client.messages.create(
                    body=f'Ok here is what I found. This article will help explain 401Ks a bit more!',
                    from_="+19126168686",
                    to=f"{users[username]}"
                )

                response.message("https://www.investopedia.com/terms/1/401kplan.asp")

            elif str(fulfillment_text) == "RRSP":
                username = get_user(str(number))
                message = client.messages.create(
                    body=f'Ok here is what I found. This article will help explain your RRSP a bit more!',
                    from_="+19126168686",
                    to=f"{users[username]}"
                )

                response.message("https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/rrsps-related-plans.html")

            elif str(fulfillment_text) == "TFSA":
                username = get_user(str(number))
                message = client.messages.create(
                    body=f'Ok here is what I found. This article will help explain your TFSA a bit more!',
                    from_="+19126168686",
                    to=f"{users[username]}"
                )

                response.message("https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/rc4466/tax-free-savings-account-tfsa-guide-individuals.html")

            elif str(fulfillment_text) == "Cryptocurrency":
                username = get_user(str(number))
                message = client.messages.create(
                    body=f'Ok here is what I found. This article will help explain cryptocurrency a bit more!',
                    from_="+19126168686",
                    to=f"{users[username]}"
                )

                response.message("https://en.wikipedia.org/wiki/Cryptocurrency")
            else:
                response.message(str(fulfillment_text))

        else:
            response.message("I'm sorry. I didn't quite catch that. Could you please rephrase your question?")

        return Response(str(response), mimetype="text/xml")



def get_user(number):
    for key, value in users.items():
         if number == value:
             return key

def detect_intent_texts(session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)

    if text:
        text_input = dialogflow.TextInput(
            text=text, language_code=language_code
        )

        query_input = dialogflow.QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(
                session=session, query_input=query_input
            )
        except InvalidArgument:
            raise

        return response.query_result.fulfillment_text, response.query_result.intent.display_name

@app.route("/trigger_price_alert", methods = ["POST", "GET"])
def trigger_price_alert():

    ticker = request.form["Ticker"]
    username = request.form["User"]
    price = request.form["Price"]

    message = client.messages.create(
        body=f'Hey {username}! We noticed that {ticker} has hit {price}! Now is your chance to buy!',
        from_="+19126168686",
        to=f"{users[username]}"
    )

    return {}
if __name__ == '__main__':
    app.run(debug=True)

