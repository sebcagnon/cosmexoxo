#!/usr/bin/env python

import sys
import Tkinter as tk
from tkFileDialog import askopenfilename

class Application(tk.Frame):
  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()
    
  def createWidgets(self):
    top = self.winfo_toplevel()
    top.geometry('600x800')
    top.configure(bg='grey')
    top.rowconfigure(0, weight=1)
    top.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)
    self.columnconfigure(0, weight=1)
    # database connection
    self.setConnectionWidgets()
      
  def dataConfigBrowser(self):
    self.dbConfigFileName.set(askopenfilename())
    
  def setConnectionWidgets(self):
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
      self.connectionStatus.set('Connected')
      self.connectButtonText.set('Disconnect')
    elif self.connectionStatus.get() == 'Connected':
      self.connectionStatus.set('Not Connected')
      self.connectButtonText.set('Connect')
    
app = Application()
app.master.title('Product Filler')
app.mainloop()

sys.exit()