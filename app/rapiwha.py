from __future__ import print_function

from email.mime.text import MIMEText
from datetime import datetime
from random import randint
from airtable import Airtable
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil.relativedelta import relativedelta
from random import randint

import time
import pandas as pd
import time
import sys
import pickle
import requests
import json
import os.path
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('./token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        return service
        
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    message = (service.users().messages().send(userId=user_id, body=message)
                .execute())
    print ('Message Id: %s' % message['id'])
    return message

pd.set_option('display.max_columns', None) # display all columns
pd.set_option('display.max_rows', 50)
pd.set_option('display.min_rows', 30)

def remove_fields(df):
    df.columns = list(map(lambda x: str.replace(x, 'fields.', ''), df.columns.values))
    return df

class WABot():    
    def __init__(self):
        self.APIUrl = 'http://panel.rapiwha.com/'
        self.token = '37YJLSDPZHSTAOM6G9QI'
   
    def send_requests(self, method, data):
        url = f"{self.APIUrl}{method}?token={self.token}"
        answer = requests.post(url, data=json.dumps(data))
        return answer.json()
    
    def get_requests(self, method, data):
        url = f"{self.APIUrl}{method}"
        data["apikey"] = self.token
        answer = requests.get(url, params=data)
        return answer.json()

    def send_message(self, phone_number, text):
        data = {"number" : phone_number,
                "text" : text}
        answer = self.get_requests('send_message.php', data)
        return answer
    
    def send_buttons(self, chatID, text, options):
        data = {"chatId" : chatID,
                "body" : text,
                "buttons" : options}
        answer = self.send_requests('sendButtons', data)
        return answer
    
    def get_dialogs(self, limit=0, page=0, order="desc"):
        data = {}
        answer = self.get_requests('get_messages.php', data)
        return answer

    def get_message_history(self, chatId='', count=100, page=0):
        data = {"count" : count,
                "page" : page,
                "chatId" : chatId}
        answer = self.get_requests('messagesHistory', data)
        return answer

    def get_all_messages(self, limit=100):
        data = {"min_time" : 1645664400,
                "limit" : 100}
        answer = self.get_requests('messagesHistory', data)
        return answer

    def welcome(self, chatID, noWelcome = False):
        welcome_string = ''
        if (noWelcome == False):
            welcome_string = "WhatsApp Demo Bot Python\n"
        else:
            welcome_string = """Incorrect command
                Commands:
                1. chatid - show ID of the current chat
                2. time - show server time
                3. me - show your nickname
                4. file [format] - get a file. Available formats: doc/gif/jpg/png/pdf/mp3/mp4
                5. ptt - get a voice message
                6. geo - get a location
                7. group - create a group with the bot"""
    
    def time(self, chatID):
        t = datetime.datetime.now()
        time = t.strftime('%d:%m:%Y')
        return self.send_message(chatID, time)

    def show_chat_id(self,chatID):
        return self.send_message(chatID, f"Chat ID : {chatID}")
    
    def processing(self):
        if self.dict_messages != []:
            for message in self.dict_messages:
                text = message['body'].split()
                if not message['fromMe']:
                    id  = message['chatId']
                    if text[0].lower() == 'hi':
                        return self.welcome(id)
                    elif text[0].lower() == 'time':
                        return self.time(id)
                    elif text[0].lower() == 'chatid':
                        return self.show_chat_id(id)
                    elif text[0].lower() == 'me':
                        return self.me(id, message['senderName'])
                    elif text[0].lower() == 'file':
                        return self.file(id, text[1])
                    elif text[0].lower() == 'ptt':
                        return self.ptt(id)
                    elif text[0].lower() == 'geo':
                        return self.geo(id)
                    elif text[0].lower() == 'group':
                        return self.group(message['author'])
                    else:
                        return self.welcome(id, True)
                else: return 'NoCommand'

    def refresh_data(self):
        dialogs = pd.json_normalize(bot.get_dialogs())

        # Hacking together to work with new API ############
        GLOW_NUMBERS = set(['19162379094'])
        TEST_NUMBERS = set([
            '923350999825',
            '23350999825',
            '13109947904'
            ])

        dialogs.rename(columns={'id':'message_id', 'text':'body'}, inplace=True)

        dialogs['id'] = dialogs.apply(lambda x: x['from'] if x['to'] in GLOW_NUMBERS else x['to'] , axis=1)
        dialogs.loc[:, 'process_date'] = pd.to_datetime(dialogs.process_date)

        dialogs = dialogs[~dialogs['id'].isin(TEST_NUMBERS)].sort_values('process_date').reset_index(drop=True)

        dialogs['last_time'] = dialogs.groupby('id').process_date.transform('max')

        dialogs['self'] = dialogs['type'].apply(lambda x: 1 if x == 'OUT' else 0)

        all_ids = dialogs['id'].unique().tolist()

        dialogs.rename(columns={'process_date':'time'}, inplace=True)

        new_dialogs = []
        for num in all_ids:
            curr_messages = dialogs[dialogs['id'] == num].copy()
            new_dialogs.append({
                'id' : num,
                'name' : num,
                'last_time' : curr_messages.last_time.max()
            })

        df_new_dialogs = pd.DataFrame(new_dialogs)

        self.dialogs = dialogs
        self.df_new_dialogs = df_new_dialogs


bot = WABot()