import Tkinter as tk
from tkFileDialog import askopenfilename

class CategoriesWidget(tk.Frame):
  """Handles display and creation of Categories from the database"""
  
  def __init__(self, master=None):
    tk.Frame.__init__(self, master, border=2, relief=tk.GROOVE)
    self.grid()
    self.createWidgets()
    self.status = 'Hide'
    
  def createWidgets(self):
    """Initialize the frame's widgets"""
    # Show or not
    self.title = tk.Label(self, text='CATEGORY EDITOR')
    self.title.grid(row=0, column=0)
    self.showButton = tk.Button(self, text='Show/Hide', command=self.showHide,
                                state=tk.DISABLED)
    self.showButton.grid(row=0, column=1)
    self.treeFrame = tk.Frame(self)
  
  def activate(self, db):
    """Enables Show/Hide Button"""
    if db:
      self.db = db
      self.showButton.config(state=tk.NORMAL)
    self.catTree = db.getCategoryTree()
    self.createButtons()
  
  def deactivate(self):
    """Hides the widget and disables button"""
    self.db = None
    self.showButton.config(state=tk.DISABLED)
    self.treeFrame.grid_forget()
  
  def showHide(self):
    """Show/Hide the whole widget"""
    if self.status == 'Show':
      self.treeFrame.grid_forget()
      self.status = 'Hide'
    else:
      self.treeFrame.grid()
      self.status = 'Show'
    
  def createButtons(self):
    """Creates the labels and buttons to edit categories"""
    self.treeFrame = tk.Frame(self)
    for child in self.catTree.leaves:
      self.recursiveLabelDisplay(child)
    
  def recursiveLabelDisplay(self, tree, column=0):
    """Recursive method that creates tabulated labels"""
    label = tk.Label(self.treeFrame, text = tree.cargo['name'])
    label.grid(column=column)
    for child in tree.leaves:
      self.recursiveLabelDisplay(child, column+1)



if __name__=='__main__':
  app = CategoriesWidget()
  app.master.title('CategoriesWidget')
  app.mainloop()
  import sys
  sys.exit()