import Tkinter as tk
import tkMessageBox

class CategoriesWidget(tk.Frame):
  """Handles display and creation of Categories from the database"""
  # CategoryWidget state constants
  HIDDEN = -1
  WAITING = 0
  EDITING = 1
  ADDING = 2
  DELETING = 3

  def __init__(self, master=None):
    tk.Frame.__init__(self, master, border=2, relief=tk.GROOVE)
    self.grid()
    self.createWidgets()
    self.editState = self.HIDDEN

  def createWidgets(self):
    """Initialize the frame's widgets"""
    # Show or not
    self.title = tk.Label(self, text='CATEGORY EDITOR')
    self.title.grid(row=0, column=0, sticky=tk.W)
    self.showButton = tk.Button(self, text='Show/Hide', command=self.showHide,
                                state=tk.DISABLED)
    self.showButton.grid(row=0, column=1, sticky=tk.E)
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
    self.editState = self.HIDDEN
    self.deleteTree()

  def showHide(self):
    """Show/Hide the whole widget"""
    if self.editState != self.HIDDEN:
      self.treeFrame.grid_forget()
      self.editState = self.HIDDEN
    else:
      self.treeFrame.grid(columnspan=2)
      self.editState = self.WAITING

  def createButtons(self):
    """Creates the labels and buttons to edit categories"""
    self.catTree = self.db.getCategoryTree()
    label = CategoryLabel(self.treeFrame,
                          name='Add main\ncategory',
                          id=-1)
    label.grid()
    for child in self.catTree.leaves:
      self.recursiveLabelDisplay(child)
    if self.editState != self.HIDDEN:
      self.editState = self.WAITING

  def recursiveLabelDisplay(self, tree, column=0):
    """Recursive method that creates tabulated labels"""
    label = CategoryLabel(self.treeFrame,
                          name=tree.cargo['name'],
                          id=tree.cargo['id'])
    label.grid(column=column, columnspan=2, sticky=tk.W)
    for child in tree.leaves:
      self.recursiveLabelDisplay(child, column+1)

  def hasChildren(self, id):
    """True if category has child categories, False if not,
    ValueError if not exist"""
    queue = self.catTree.leaves[:]
    while queue:
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
    self.deleteTree()
    self.createButtons()

  def deleteTree(self):
    """Deletes the category tree"""
    for child in self.treeFrame.winfo_children():
      child.destroy()


class CategoryLabel(tk.Frame):
  """Labels with right-click menu for editing"""

  def __init__(self, master=None, name='', id=-1):
    self.textVar = tk.StringVar()
    self.textVar.set(str(id) + ': ' + name)
    self.id = id
    tk.Frame.__init__(self, master)
    self.label = tk.Label(self, textvariable=self.textVar,
                      bg='white', bd=1, relief=tk.RAISED)
    self.label.grid()
    # create right-click menu
    self.menu = tk.Menu(self, tearoff=0)
    if self.id!=-1: # id=-1 for buttons only
      self.menu.add_command(label='Edit', command=self.edit)
    self.menu.add_command(label='Add subcategory',
                          command=self.add_subcategory)
    if self.id!=-1:
      self.menu.add_command(label='Delete', command=self.delete)
    self.label.bind('<Button-3>', self.openMenu)
    # shortcut
    self.mainFrame = self.master.master

  def openMenu(self, event):
    """Opens the right click menu for the label"""
    if self.mainFrame.editState == self.mainFrame.WAITING:
      self.menu.post(event.x_root, event.y_root)

  def edit(self):
    """Create edition frame to edit current category name"""
    self.mainFrame.editState = self.mainFrame.EDITING
    self.label.grid_forget()
    message = 'Edit Category Name:'
    self.newName = tk.StringVar()
    self.editFrame = NewCategoryFrame(master=self,
                        textVar=self.newName,
                        labelText=message,
                        buttonText='Edit',
                        buttonAction=self.editCategory)
    self.editFrame.grid(columnspan=2)
    self.config(bd=2, relief=tk.SUNKEN)

  def editCategory(self):
    """when the NewCategoryFrame.addButton is clicked"""
    res = self.mainFrame.db.editCategory(self.newName.get(), self.id)
    if res==True:
      self.mainFrame.updateTree()
      self.mainFrame.editState = self.mainFrame.WAITING
    else:
      tkMessageBox.showerror('Edit Category Error',
            'Category could not be edited\n' + str(res))

  def add_subcategory(self):
    """Create edition frame to add subcategory to current one"""
    self.mainFrame.editState = self.mainFrame.ADDING
    if self.id == -1:
      message = 'New category:'
    else:
      message = 'New Subcategory:'
    self.catName = tk.StringVar()
    self.editFrame = NewCategoryFrame(master=self,
                        textVar=self.catName,
                        labelText=message,
                        buttonText='Add',
                        buttonAction=self.addCategory)
    self.editFrame.grid(row=0, column=1, columnspan=2, rowspan=3)
    self.config(bd=2, relief=tk.SUNKEN)

  def addCategory(self):
    """when the NewCategoryFrame.addButton is clicked"""
    res = self.mainFrame.db.addCategory(self.catName.get(), self.id)
    if res==True:
      self.mainFrame.updateTree()
      self.mainFrame.editState = self.mainFrame.WAITING
    else:
      tkMessageBox.showerror('Add Category Error',
            'Category could not be created\n' + str(res))

  def cancelAddCategory(self):
    """when the NewCategoryFrame.cancelButton is clicked"""
    self.editFrame.destroy()
    self.mainFrame.editState = self.mainFrame.WAITING
    self.config(bd=0, relief=tk.FLAT)

  def delete(self):
    """Delete the category if user confirms"""
    self.mainFrame.editState = self.mainFrame.DELETING
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
    self.mainFrame.editState = self.mainFrame.WAITING


class NewCategoryFrame(tk.Frame):
  """A frame for creating a new category"""

  def __init__(self, master=None, textVar=None, labelText='',
                buttonText='', buttonAction=None):
    if not textVar:
      self.textVar = tk.StringVar()
    else:
      self.textVar = textVar
    tk.Frame.__init__(self, master)
    # Label explanation
    self.label = tk.Label(self, text=labelText)
    self.label.grid(columnspan=2)
    self.entry = tk.Entry(self, textvariable=self.textVar)
    self.entry.grid(columnspan=2)
    # Entry focus and Return key reaction
    self.entry.focus_set()
    def entryAction(event):
      """Ditch the event, call buttonAction"""
      buttonAction()
    self.entry.bind("<Return>", entryAction)
    # Buttons
    self.addButton = tk.Button(self, text=buttonText,
        command=buttonAction)
    self.addButton.grid(row=2, column=0)
    self.cancelButton = tk.Button(self, text='Cancel',
        command=self.master.cancelAddCategory)
    self.cancelButton.grid(row=2, column=1)


if __name__=='__main__':
  app = CategoriesWidget()
  app.master.title('CategoriesWidget')
  app.mainloop()
  import sys
  sys.exit()