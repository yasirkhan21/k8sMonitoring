import requests
import json
from notifyviaEmail import *

webhooks = {
}

receivers = ""
senderEmail = 'singhpranshu650@gmail.com@gmail.com'
alwaysInCc = ""
fallbackurl = ""

def notify(content):
    try:      
        message = f'<h1><strong>Status: {content["Status"]}</strong></h1><br>Deployment: {content["Deployment"]}<br>Namespace: {content["Namespace"]}<br>Reason: {content["Reason"]}'
        print(message)
        payload = json.dumps({
        "text": message
        })
        headers = {
        'Content-Type': 'application/json'
        }
        webhookurl = fallbackurl
        if webhooks.get(content["Namespace"]):
            webhookurl = webhooks[ content[ "Namespace" ] ]
        response = requests.request("POST", webhookurl, headers=headers, data=payload)
        if receivers:
            service = getService()
            emailMessage = create_message(senderEmail, receivers, cc, content["Namespace"]+ ' ' + 'monitoring', message)
            msgid, err = send_message(service=service, user_id='me',message=emailMessage)
            if err is None == False:
                service = getService()
                emailMessage = create_message(senderEmail, receivers, cc, content["Namespace"]+ ' ' + 'monitoring', message)
                send_message(service=service, user_id='me',message=emailMessage)
        print(response.text)
    except Exception as e:
        print(e)