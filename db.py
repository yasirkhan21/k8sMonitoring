import mysql.connector
from mysql.connector import errorcode
import sys


def getDbConnection():
    try:
      # cnx = mysql.connector.connect(**config)
      cnx = mysql.connector.connect( user= '',
              password= '',
              host= '', 
              database= '',
              raise_on_warnings= True)
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
      sys.exit("database is not connected")  
    else:
        return cnx

def save(cnx, namespace, name, reason, message, date, tablename):
    try: 
        cursor = cnx.cursor()
        add_Logs_to_mysql = ("INSERT INTO " + tablename +
        " (namespace, deployment, status, reason, date) "
        "VALUES (%s, %s, %s, %s, %s)")
        data_Logs = (namespace, name, reason, message, date)
        cursor.execute(add_Logs_to_mysql, data_Logs)
        cnx.commit()
        cursor.close()
        return True   
    except Exception as e:
      print(e)
      return False    
  
def getLog(fromDate, tilldate, tableName):
  try:
    cnx = getDbConnection()
    cursor = cnx.cursor()
    query = ("SELECT * FROM  " + tableName+
         " WHERE date BETWEEN %s AND %s")
    cursor.execute(query,(fromDate, tilldate))
    arr = []
    for (_id, namespace, deployment, status, reason, date) in cursor:
      arr.append({ "namespace": namespace, "deployment": deployment, "status": status, "reason": reason, "date": date })
    cursor.close()
    cnx.close()
    return arr       
  except Exception as e:
    cursor.close()
    cnx.close()
    print(e)
