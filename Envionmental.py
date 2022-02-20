from flask import Flask, request, Response
from twilio.twiml.messaging_response import Message, MessagingResponse
import json
import threading as th
from google.cloud import dialogflow
import os
from google.api_core.exceptions import InvalidArgument

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "zoomerJSONFile.json"

## FLAG ----------------------------------------------------
DIALOGFLOW_PROJECT_ID = 'zoomer-341817'
DIALOGFLOW_LANGUAGE_CODE = 'en'


with open('user_db.json', 'r') as db:
    users = json.load(db)



# def return_sms():
#
#     number = request.form["From"]
#     message_body = request.form["Body"]
#
#     response = MessagingResponse()
#
#     # If using a new number
#     if number not in users.values():
#         response.message(body=f"Hi there! I don't recognize this number. What would you like me to call you?")
#         users[f"temp_{str(number)}"] = str(number)
#         return Response(str(response), mimetype="text/xml")
#
#     # Register new number under a name
#     if f"temp_{str(number)}" in users.keys():
#         project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
#         fulfullment_text = detect_intent_texts(f"{number}", message_body, 'en')
#         response.message(body=f"Ok {str(fulfullment_text)}! I will remember your name from here on out! "
#                               f"It is very nice to meet you! I'm here to help make investing in the stock market easier, simpler, and more convenient!"
#                               f"Please let me know what I can do for you!")
#
#         users[fulfullment_text] = users.pop(f"temp_{str(number)}")
#         return Response(str(response), mimetype="text/xml")
#
#
#     #------Execute NLP Stuff to figure out intent
#


    #return Response(str(response), mimetype="text/xml")


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

        return response.query_result



text_sample = "What is the price of Anthem?"
project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
fulfullment_text = detect_intent_texts("me", text_sample, 'en')
response.message(body=f"Ok {str(fulfullment_text)}! I will remember your name from here on out! "
                      f"It is very nice to meet you! I'm here to help make investing in the stock market easier, simpler, and more convenient!"
                      f"Please let me know what I can do for you!")

