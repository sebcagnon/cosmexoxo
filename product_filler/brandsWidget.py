import Tkinter as tk
from treeWidget import TreeWidget
from textEditFrame import TextEditFrame
import tkMessageBox

class BrandsWidget(TreeWidget):
  """Handles display and creation of Categories from the database"""

  def createButtons(self):
    """Creates the labels and buttons to edit categories"""
    self.brandTree = self.db.getBrandTree()
    label = BrandLabel(master=self.treeFrame,
                          name='Add New\nBrand',
                          id=-1,
                          type=None,
                          navbar=None)
    label.grid(sticky=tk.W)
    for child in self.brandTree.leaves:
      self.recursiveLabelDisplay(child)
    if self.editState != self.HIDDEN:
      self.editState = self.WAITING

  def recursiveLabelDisplay(self, tree, column=0):
    """Recursive method that creates tabulated labels"""
    if column == 0:
      type = 'company'
    else:
      type = 'brand'
    label = BrandLabel(master=self.treeFrame,
                          name=tree.cargo['name'],
                          id=tree.cargo['id'],
                          navbar=tree.cargo['in_navbar'],
                          type=type)
    label.grid(column=column, sticky=tk.W)
    for child in tree.leaves:
      self.recursiveLabelDisplay(child, column+1)


class BrandLabel(tk.Frame):
  """Labels with right-click menu for editing"""

  def __init__(self, name, id, navbar, type, master=None):
    """
    master: the parent widget
    name: the name of the brand/company (str)
    id: the id of the brand/company, -1 for the "add company" label (int)
    navbar: in_navbar status (bool)
    type: 'company' or 'brand'
    """
    tk.Frame.__init__(self, master)
    # create name label
    self.textVar = tk.StringVar()
    self.textVar.set(str(id) + ': ' + str(name))
    self.id = id
    self.navbar = navbar
    self.type = type
    self.label = tk.Label(self, textvariable=self.textVar,
                      bg='white', bd=1, relief=tk.RAISED)
    self.label.grid(row=0)
    # create navbar checkbox
    if self.id != -1:
      self.navLabel = tk.Label(self, text="In Navbar?")
      self.navLabel.grid(row=0, column=1)
      self.navState = tk.IntVar()
      self.navState.set(self.navbar*1)
      self.navbarCheck = tk.Checkbutton(self, variable=self.navState)
      self.navbarCheck.grid(row=0, column=2)
      self.navbarCheck.bind('<Button-1>', self.navbarCheckHandler)
    # create right-click menu
    if 0:
      self.menu = tk.Menu(self, tearoff=0)
      if self.id!=-1: # id=-1 for buttons only
        self.menu.add_command(label='Edit', command=self.edit)
      self.menu.add_command(label='Add brand',
                            command=self.add_brand)
      if self.id!=-1:
        self.menu.add_command(label='Delete', command=self.delete)
      self.label.bind('<Button-3>', self.openMenu)
    # shortcut
    self.mainFrame = self.master.master

  def navbarCheckHandler(self, event):
    """Edits the in_navbar info when checkbutton is clicked"""
    self.mainFrame.editState == self.mainFrame.EDITING
    res = self.mainFrame.db.editLineFromId(table=self.type, 
                                         column='in_navbar',
                                         newValue=(not self.navbar),
                                         id=self.id)
    if res==True:
      self.mainFrame.updateTree()
    else:
      tkMessageBox.showerror('Edit Company/Brand Error',
            'Navbar setting could not be edited\n' + str(res))
    self.mainFrame.editState = self.mainFrame.WAITING

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




if __name__=='__main__':
  app = BrandsWidget()
  app.master.title('BrandsWidget')
  app.mainloop()
  import sys
  sys.exit()