from kubernetes import client, config, watch
import time
import requests
import json
from notify import notify
# from notifyviaEmail import *
import datetime
# from functions import NamespaceWithTimeStamp
# from db import save, getDbConnection
searchedNameSpacesMemo = []
# cnx = getDbConnection()
config.load_kube_config()
v1 = client.CoreV1Api()

headers = {
        'Content-Type': 'application/json'
        }
webhookurl = ""
w = watch.Watch()

senderEmail = 'alerts@gmail.com'
receivers = 'pranshu.singh@b.in'
# receivers = 'pranshu.singh@bajajfinserv.in'
cc = ''
subject = "container restart alerts!!!"

notToNotify = [
]

def restartsAlert():
 for event in w.stream(v1.list_event_for_all_namespaces, _request_timeout=60):
   try:
    if event.get("object").reason == 'BackOff' and event.get("object").message == 'Back-off restarting failed container':
        print(event.get("object").involved_object.name)
        deployment = event.get("object").involved_object.name.split('-') 
        deployment.pop()
        deployment.pop()
        deployment = '-'.join(deployment)
        if deployment[len(deployment) -1] == '-':
          deployment = deployment.split('-')
          deployment.pop()
          deployment.pop()
          deployment = '-'.join(deployment) 
        pod = v1.read_namespaced_pod_status(name = event.get("object").involved_object.name, namespace =event.get("object").involved_object.namespace)
        if pod.metadata.owner_references[0].kind == 'Job':
          continue
        if deployment in notToNotify:
          continue
        willNotify = True
        for index,obj in enumerate(searchedNameSpacesMemo):
          if obj.Deployment == deployment and obj.timeStamp+7200 > time.time():
            willNotify = False
            break 
          elif obj.Deployment == deployment and obj.timeStamp+7200 <= time.time():
            # remove from searchedNameSpacesMemo if it has been more than 2 hours for same deployment``
            searchedNameSpacesMemo.pop(index)
        if willNotify == False:
          continue 
        content={
          "Namespace": event.get("object").involved_object.namespace,
          "Deployment": deployment,
          "Status": event.get("object").reason,
          "Reason": event.get("object").message,
          # "Deployment":item.metadata.labels['app']
        }  
        # print(content)
        # continue
        api = client.CustomObjectsApi()
        resource = api.list_namespaced_custom_object(group="metrics.k8s.io",version="v1beta1", namespace=event.get("object").involved_object.namespace, plural="pods")
        for podUtilisation in resource['items']:
          if len(podUtilisation['containers']) == 1:
            if podUtilisation['metadata']['name'] == event.get("object").involved_object.name:
                content['Reason'] += '.  '
                content['Reason'] += 'cpu:  ' + str(podUtilisation['containers'][0]['usage']['cpu']) + '  memory:  ' + str(podUtilisation['containers'][0]['usage']['memory']) + '.'
                break 
        if event.get("object").involved_object.name is not None:
          content['Reason'] +=  'PodName: ' + event.get("object").involved_object.name      
        print(content)       
        date = datetime.datetime.now()
        # data_saved = save(cnx, content["Namespace"], deployment, content["Status"], content["Reason"], date, "aks_restarts")
        # # retry once again
        # if data_saved == False:
        #     cnx.reconnect(attempts=1, delay=0)
        #     save(cnx, content["Namespace"], deployment, content["Status"], content["Reason"], date, "aks_restarts")
        # payload = f'<h1><strong>Status: {content["Status"]}</strong></h1><br>Deployment: {content["Deployment"]}<br>Namespace: {content["Namespace"]}<br>Reason: {content["Reason"]}'    
        # response = requests.request("POST", webhookurl, headers=headers, data=json.dumps({ "text": payload }))
        # if receivers:
        #     service = getService()
        #     emailMessage = create_message(senderEmail, receivers, cc, subject, payload)
        #     msgid, err = send_message(service=service, user_id='me',message=emailMessage)
        #     # retry once again
        #     if err is None == False:
        #         service = getService()
        #         emailMessage = create_message(senderEmail, receivers, cc, subject, payload)
        #         send_message(service=service, user_id='me',message=emailMessage)
        currEpochTime = time.time()            
        searchedNameSpacesMemo.append(NamespaceWithTimeStamp(Deployment=deployment, timeStamp=currEpochTime)) 
   except Exception as e:
    print(e)           
 
 
 
def run():
  try:
    restartsAlert()
  except Exception as e:
    print("Some exception occured")
    print("Trying to recover")
    if str(e) == "HTTPSConnectionPool(host='centralindia.azmk8s.io', port=443): Read timed out.":
        time.sleep(60)
        print("restarted")
        run()
    else:
      print("cannot be recovered. please restart script.")  
      print(e)


run() 
 
 
