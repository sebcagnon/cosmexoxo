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
    # select db connection file
    self.browseButton = tk.Button(self, text='Browse...',
      command=self.fileBrowser)
    self.dbConfigFileName = tk.StringVar()
    self.fileEntry = tk.Entry(self, 
      textvariable=self.dbConfigFileName)
    self.browseButton.grid(row=0, column=0, rowspan=1)
    self.fileEntry.grid(row=0, column=1, rowspan=5)
      
  def fileBrowser(self):
    self.dbConfigFileName.set(askopenfilename())
    
app = Application()
app.master.title('Product Filler')
app.mainloop()

sys.exit()