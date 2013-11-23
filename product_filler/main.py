#!/usr/bin/env python

import sys
import os
import Tkinter as tk
from tkFileDialog import askopenfilename
import dbConnect
import connectionWidget
import categoriesWidget
import brandsWidget

APP_PATH = r'c:\Users\luluseb\Documents\cosmexoxo\product_filler'

class Application(tk.Frame):
  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
    self.createWidgets()
    self.db = None

  def createWidgets(self):
    top = self.winfo_toplevel()
    top.configure(bg='grey')
    top.rowconfigure(0, weight=1)
    top.columnconfigure(0, weight=1)
    self.rowconfigure(0, weight=1)
    self.columnconfigure(0, weight=1)
    # database connection
    self.connectionWidget = connectionWidget.ConnectionWidget(self)
    self.categoriesWidget = \
          categoriesWidget.CategoriesWidget('CATEGORY EDITOR', self)
    self.brandsWidget = \
          brandsWidget.BrandsWidget('COMPANIES/BRANDS EDITOR', self)

    self.bind('<<Connection>>', self.onConnected)
    self.bind('<<Disconnection>>', self.onDisconnected)
    top.iconbitmap(os.path.join(APP_PATH, 'favicon.ico'))

  def onConnected(self, event):
    """Activates the widgets once you are connected"""
    self.db = self.connectionWidget.db
    self.categoriesWidget.activate(self.db)
    self.brandsWidget.activate(self.db)

  def onDisconnected(self, event):
    """Deactivates the widgets once you are disconnected"""
    self.db = None
    self.categoriesWidget.deactivate()
    self.brandsWidget.deactivate()

if __name__=='__main__':
  app = Application()
  app.master.title('Product Filler')
  app.mainloop()
  if app.db:
    app.db.closeConnection()
  sys.exit()