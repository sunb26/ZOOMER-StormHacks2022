from flask import Flask, request, Response
from twilio.twiml.messaging_response import Message, MessagingResponse
import json
import threading as th
from google.cloud import dialogflow
import os
from google.api_core.exceptions import InvalidArgument

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "zoomerJSONFile.json"

## FLAG ----------------------------------------------------
DIALOGFLOW_LANGUAGE_CODE = 'en'


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
        # with open('user_db.json', 'w') as db:
        #     json.dump(users, db)

        return Response(str(response), mimetype="text/xml")

    # Register new number under a name
    if f"temp_{str(number)}" in users.keys():
        project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
        fulfillment_text = detect_intent_texts(f"{number}", message_body, 'en')
        response.message(body=f"Hey there {str(fulfillment_text)}! I will remember your name from here on out! "
                              f"It is very nice to meet you! I'm here to help make investing in the stock market easier, simpler, and more convenient!"
                              f" Please let me know what I can do for you!")

        users[fulfillment_text] = users.pop(f"temp_{str(number)}")
        # with open('user_db.json', 'w') as db:
        #     json.dump(users, db)

        return Response(str(response), mimetype="text/xml")
    else:


        return Response(str(response), mimetype="text/xml")



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

        return response.query_result.fulfillment_text

# @app.route('/trigger-price-alert', methods=["POST", "GET"])
# def create_price_alert():
#
#     action = request.form["Action"]
#
#     def start_timer():
#         if action == "Cancel":
#             timer.cancel()
#         else:
#             ## API CALL HERE ##
#
#
#     timer = th.Timer(10, start_timer)
#



if __name__ == '__main__':
    app.run(debug=True)

