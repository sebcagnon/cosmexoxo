import Tkinter as tk
from tkFileDialog import askopenfilename
import dbConnect

class ConnectionWidget(tk.Frame):
  """Handles connection to database server"""
  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()

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
    if self.connectionStatus.get() == 'Not Connected':
      self.connectionStatus.set('Connecting...')
      self.conn, self.cur, err = dbConnect.connect(self.dbConfigFileName.get())
      if err:
        self.connectionStatus.set('ConnectionFailed')
      else:
        self.connectionStatus.set('Connected')
        self.connectButtonText.set('Disconnect')
    elif self.connectionStatus.get() == 'Connected':
      self.connectionStatus.set('Disconnecting')
      dbConnect.closeConnection(self.conn, self.cur)
      self.connectionStatus.set('Not Connected')
      self.connectButtonText.set('Connect')

  def dataConfigBrowser(self):
    self.dbConfigFileName.set(askopenfilename())

if __name__=='__main__':
  app = ConnectionWidget()
  app.master.title('ConnectionWidget')
  app.mainloop()
  import sys
  sys.exit()