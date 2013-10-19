import psycopg2
import json

class DBConnection(Object):
  """handles connection and common requests to the database"""

  def __init__(self, dataBaseConfig):
    """dataBaseConfig: path to JSON file with db address and authentication data"""
    [self.conn, self.cur] = self.connect(file)


  def connect(self.file):
    """ Connects to a database using a json file for the parameters """
    jsonFile = open(file)
    params = json.load(jsonFile)
    jsonFile.close()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    return [conn, cur]
    
  def closeConnection(self):
    """Disconnects from database"""
    self.cur.close()
    self.conn.close()
