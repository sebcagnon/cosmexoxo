import Tkinter as tk
from tkFileDialog import askopenfilename
import dbConnect
import json
import boto

class ConnectionWidget(tk.Frame):
  """Handles connection to database server"""
  def __init__(self, master=None):
    tk.Frame.__init__(self, master, border=2, relief=tk.GROOVE)
    self.grid(sticky=tk.N+tk.E+tk.W)
    self.createWidgets()
    self.connectionKeys = {}

  def createWidgets(self):
    """ select db connection file and connect button """
    # text variables
    self.dbConfigFileName = tk.StringVar()
    self.connectionStatus = tk.StringVar()
    self.connectionStatus.set('Not Connected')
    self.connectButtonText = tk.StringVar()
    self.connectButtonText.set('Connect')

    # file selection
    self.browseButton = tk.Button(self, text='Browse...',
      command=self.dataConfigBrowser)
    self.fileEntry = tk.Entry(self,
      textvariable=self.dbConfigFileName)
    self.browseButton.grid(row=0, column=0, columnspan=1)
    self.fileEntry.grid(row=0, column=1, columnspan=3)

    # connection
    self.connectButton = tk.Button(self,
      textvariable=self.connectButtonText,
      command=self.connectToDatabase)
    self.connectStatusLabel = tk.Label(self,
      textvariable=self.connectionStatus)
    self.connectButton.grid(row=1, column=0)
    self.connectStatusLabel.grid(row=1, column=1)

  def connectToDatabase(self):
    """Handler of the 'connect' button, connects or disconnects from db"""
    if self.connectionStatus.get() != 'Connected':
      self.connectionStatus.set('Connecting...')
      try:
        jsonFile = open(self.dbConfigFileName.get().encode('utf-8'), 'r')
        self.connectionKeys = json.load(jsonFile)
        jsonFile.close()
        self.db = dbConnect.DBConnection(self.connectionKeys['database'])
        self.s3 = boto.connect_s3(**self.connectionKeys['aws_access_key'])
        self.bucket = self.s3.get_bucket(self.connectionKeys['s3_bucket'])
      except:
        self.connectionStatus.set('ConnectionFailed')
        raise
      else:
        if self.master:
          self.master.event_generate('<<Connection>>')
        self.connectionStatus.set('Connected')
        self.connectButtonText.set('Disconnect')
    elif self.connectionStatus.get() == 'Connected':
      if self.master:
        self.master.event_generate('<<Disconnection>>')
      self.connectionStatus.set('Disconnecting')
      self.db.closeConnection()
      self.connectionStatus.set('Not Connected')
      self.connectButtonText.set('Connect')

  def dataConfigBrowser(self):
    """File selector for database info"""
    self.dbConfigFileName.set(askopenfilename())

if __name__=='__main__':
  app = ConnectionWidget()
  app.master.title('ConnectionWidget')
  app.mainloop()
  import sys
  sys.exit()