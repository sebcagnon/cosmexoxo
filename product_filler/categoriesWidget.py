import Tkinter as tk
from tkFileDialog import askopenfilename

class CategoriesWidget(tk.Frame):
  """Handles display and creation of Categories from the database"""
  
  def __init__(self, master=None):
    tk.Frame.__init__(self, master, border=2, relief=tk.GROOVE)
    self.grid()
    self.createWidgets()
    self.visibility = 'Hide'
    
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
    if self.visibility == 'Show':
      self.treeFrame.grid_forget()
      self.visibility = 'Hide'
    else:
      self.treeFrame.grid()
      self.visibility = 'Show'
    
  def createButtons(self):
    """Creates the labels and buttons to edit categories"""
    self.treeFrame = tk.Frame(self)
    for child in self.catTree.leaves:
      self.recursiveLabelDisplay(child)
    
  def recursiveLabelDisplay(self, tree, column=0):
    """Recursive method that creates tabulated labels"""
    label = CategoryLabel(self.treeFrame,
                          name=tree.cargo['name'],
                          id=tree.cargo['id'])
    label.grid(column=column)
    for child in tree.leaves:
      self.recursiveLabelDisplay(child, column+1)


class CategoryLabel(tk.Label):
  """Labels with right-click menu for editing"""
  
  def __init__(self, master=None, name='', id=-1):
    self.textVar = tk.StringVar()
    self.textVar.set(name)
    self.id = id
    tk.Label.__init__(self, master, textvariable=self.textVar,
                      bg='white', bd=1, relief=tk.RAISED)
    # create right-click menu
    self.menu = tk.Menu(self, tearoff=0)
    self.menu.add_command(label='Edit', command=self.edit)
    self.menu.add_command(label='Add subcategory', 
                          command=self.add_subcategory)
    self.menu.add_command(label='Delete', command=self.delete)
    self.bind('<Button-3>', self.openMenu)
  
  def openMenu(self, event):
    """Opens the right click menu for the label"""
    self.menu.post(event.x_root, event.y_root)
  
  def edit(self):
    """Edit the name of the category"""
    print 'edit ' + self.textVar.get()
  
  def add_subcategory(self):
    """Add a new child category to the current one"""
    print 'add_subcategory to ' + self.textVar.get()
  
  def delete(self):
    """Delete the category if user confirms"""
    print 'delete ' + self.master.master.visibility
    

if __name__=='__main__':
  app = CategoriesWidget()
  app.master.title('CategoriesWidget')
  app.mainloop()
  import sys
  sys.exit()