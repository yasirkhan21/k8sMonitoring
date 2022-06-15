from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError
# from onceinadayalert import isNowInTimePeriod
# import time
# import datetime
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']

def getService():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
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

    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message(sender, to, cc, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text,'html')
  message['to'] =  to
  message['from'] = sender
  message['Cc'] = cc
  message['subject'] = subject
  return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}    

  
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
  try:
    # checking if it does not collide with onceinadayalert 
    # if isNowInTimePeriod(time(checkingHour-1,58),time(checkingHour,2),datetime.now().time()):
    #   time.sleep(240)
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('id',message['id'])
    return  message['id'],None 
  except HttpError as error:
    print( 'err',error)
    return None, error           
