import psycopg2
import json

def connect(file):
  """ Connects to a database using a json file for the parameters """
  try:
    jsonFile = open(file)
    params = json.load(jsonFile)
    jsonFile.close()
  except IOError, e:
    print 'File Error:', e
    return [False, False, e]
  try:
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
  except OperationalError, e:
    print 'Connection Error:', e
    return [False, False, e]
  return [conn, cur, False]
    
def closeConnection(conn, cur):
  cur.close()
  conn.close()
  