import Tkinter as tk
from treeWidget import TreeWidget
from textEditFrame import TextEditFrame
import tkMessageBox

class BrandsWidget(TreeWidget):
  """Handles display and creation of Categories from the database"""
  # CategoryWidget state constants
  HIDDEN = -1
  WAITING = 0
  EDITING = 1
  ADDING = 2
  DELETING = 3

  def createButtons(self):
    """Creates the labels and buttons to edit categories"""
    self.brandTree = self.db.getBrandTree()
    label = BrandLabel(self.treeFrame,
                          name='Add New\nBrand',
                          id=-1)
    label.grid()
    for child in self.brandTree.leaves:
      self.recursiveLabelDisplay(child)
    if self.editState != self.HIDDEN:
      self.editState = self.WAITING

  def recursiveLabelDisplay(self, tree, column=0):
    """Recursive method that creates tabulated labels"""
    label = BrandLabel(self.treeFrame,
                          name=tree.cargo['name'],
                          id=tree.cargo['id'])
    label.grid(column=column, sticky=tk.W)
    for child in tree.leaves:
      self.recursiveLabelDisplay(child, column+1)


class BrandLabel(tk.Frame):
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
    return
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
  app = CategoriesWidget()
  app.master.title('CategoriesWidget')
  app.mainloop()
  import sys
  sys.exit()