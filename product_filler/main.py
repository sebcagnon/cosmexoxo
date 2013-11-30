#!/usr/bin/env python

import sys
import os
import Tkinter as tk
from tkFileDialog import askopenfilename
import dbConnect
import connectionWidget
import categoriesWidget
import brandsWidget
import productWidget

APP_PATH = r'c:\Users\luluseb\Documents\cosmexoxo\product_filler'

class Application(tk.Frame):
  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
    self.path = APP_PATH
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
    self.productWidget = \
          productWidget.ProductWidget('PRODUCT EDITOR', self)

    self.bind('<<Connection>>', self.onConnected)
    self.bind('<<Disconnection>>', self.onDisconnected)
    top.iconbitmap(os.path.join(self.path, 'resources', 'favicon.ico'))

  def onConnected(self, event):
    """Activates the widgets once you are connected"""
    self.db = self.connectionWidget.db
    self.bucket = self.connectionWidget.bucket
    self.categoriesWidget.activate(self.db)
    self.brandsWidget.activate(self.db)
    self.productWidget.activate(self.db, self.bucket)

  def onDisconnected(self, event):
    """Deactivates the widgets once you are disconnected"""
    self.db = None
    self.categoriesWidget.deactivate()
    self.brandsWidget.deactivate()
    self.productWidget.deactivate()

if __name__=='__main__':
  app = Application()
  app.master.title('Product Filler')
  app.mainloop()
  if app.db:
    app.db.closeConnection()
  sys.exit()