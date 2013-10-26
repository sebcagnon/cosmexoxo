import Tkinter as tk
import tkMessageBox

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
    self.catTree = self.db.getCategoryTree()
    label = CategoryLabel(self.treeFrame,
                          name='Add main\ncategory',
                          id=-1)
    label.grid()
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
      
  def hasChildren(self, id):
    """True if category has child categories, False if not, 
    ValueError if not exist"""
    queue = self.catTree.leaves[:]
    while queue:
      print queue
      node = queue.pop(0)
      if node.cargo['id']==id:
        if node.leaves:
          return True
        else:
          return False
      else:
        queue += node.leaves[:]
    raise ValueError('Could not find category with this id: ' + str(id))
  
  def updateTree(self):
    """Updates the category tree and the labels"""
    for child in self.treeFrame.winfo_children():
      child.destroy()
    self.createButtons()


class CategoryLabel(tk.Label):
  """Labels with right-click menu for editing"""
  
  def __init__(self, master=None, name='', id=-1):
    self.textVar = tk.StringVar()
    self.textVar.set(str(id) + ': ' + name)
    self.id = id
    tk.Label.__init__(self, master, textvariable=self.textVar,
                      bg='white', bd=1, relief=tk.RAISED)
    # create right-click menu
    self.menu = tk.Menu(self, tearoff=0)
    if self.id!=-1: # id=-1 for buttons only
      self.menu.add_command(label='Edit', command=self.edit)
    self.menu.add_command(label='Add subcategory', 
                          command=self.add_subcategory)
    if self.id!=-1:
      self.menu.add_command(label='Delete', command=self.delete)
    self.bind('<Button-3>', self.openMenu)
    # shortcut
    self.mainFrame = self.master.master
  
  def openMenu(self, event):
    """Opens the right click menu for the label"""
    self.menu.post(event.x_root, event.y_root)
  
  def edit(self):
    """Edit the name of the category"""
    print 'edit ' + self.textVar.get()
  
  def add_subcategory(self):
    """Add a new child category to the current one"""
    if self.id == -1:
      message = 'Create new category'
    else:
      message = 'Create new category under: ' + self.textVar.get()
    self.catName = tk.StringVar()
    self.editWindow = EditCategoryWindow(master=self, 
                        textVar=self.catName,
                        labelText=message,
                        buttonText='Add')
  
  def delete(self):
    """Delete the category if user confirms"""
    if self.mainFrame.hasChildren(self.id):
      tkMessageBox.showerror('DeleteCategory Error',
          'Can not delete ' + self.textVar.get()
          + '\nDelete subcategories first')
    elif tkMessageBox.askyesno('Delete Category Warning',
            'Warning: if you delete a category\n' +
            'it can create broken links\n' +
            'Confirm delete?',
            icon=tkMessageBox.WARNING):
      res = self.mainFrame.db.deleteCategory(self.id)
      if res==True:
        tkMessageBox.showinfo('Delete Category Success',
            'Category was successfully deleted')
        self.mainFrame.updateTree()
      else:
        tkMessageBox.showerror('Delete Category Error',
            'Category could not be deleted\n' + str(res))


class EditCategoryWindow(tk.Toplevel):
  """A pop-up window that enables category editing"""
  
  def __init__(self, master=None, textVar=None, labelText='', buttonText=''):
    if not textVar:
      self.textVar = tk.StringVar()
    else:
      self.textVar = textVar
    tk.Toplevel.__init__(self, master)
    self.geometry('300x300')
    self.label = tk.Label(self, text=labelText)
    self.label.grid(columnspan=2)
    self.entry = tk.Entry(self, textvariable=self.textVar)
    self.entry.grid(columnspan=2)
    self.addButton = tk.Button(self, text=buttonText, command=self.add)
    self.addButton.grid(row=2, column=0)
    self.cancelButton = tk.Button(self, text='Cancel', command=self.cancel)
    self.cancelButton.grid(row=2, column=1)
  
  def cancel(self):
    """Closes the window without modification"""
    self.destroy()
  
  def add(self):
    """Closes window with signal to act the changes"""
    self.destroy()

if __name__=='__main__':
  app = CategoriesWidget()
  app.master.title('CategoriesWidget')
  app.mainloop()
  import sys
  sys.exit()