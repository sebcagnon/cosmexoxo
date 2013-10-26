#!/usr/bin/env python

import sys
import os
import Tkinter as tk
from tkFileDialog import askopenfilename
import dbConnect
import connectionWidget

APP_PATH = r'c:\Users\luluseb\Documents\cosmexoxo\product_filler'

class Application(tk.Frame):
  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid()
    self.createWidgets()
    self.db = None

  def createWidgets(self):
    top = self.winfo_toplevel()
    top.geometry('600x800')
    top.configure(bg='grey')
    top.rowconfigure(0, weight=1)
    top.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)
    self.columnconfigure(0, weight=1)
    # database connection
    self.connectionWidget = connectionWidget.ConnectionWidget(self)

    self.bind('<<Connection>>', self.onConnected)
    self.bind('<<Disconnection>>', self.onDisconnected)
    top.iconbitmap(os.path.join(APP_PATH, 'favicon.ico'))

  def onConnected(self, event):
    """Activates the widgets once you are connected"""
    self.db = self.connectionWidget.db
    
  def onDisconnected(self, event):
    """Deactivates the widgets once you are disconnected"""
    self.db = None


app = Application()
app.master.title('Product Filler')
app.mainloop()

sys.exit()