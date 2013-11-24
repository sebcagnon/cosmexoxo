import os
import dbConnect
import Tkinter as tk
from baseWidget import BaseWidget

class ProductWidget(BaseWidget):
  """Widget for editing products"""

  def createButtons(self):
    """Creates the edition fields for the product"""
    # Images
    imagePath = os.path.join(self.master.path, "resources", "plus_icon.gif")
    self.plusImage = tk.PhotoImage(file=imagePath)
    deleteImagePath = os.path.join(self.master.path, "resources",
                       "minus_icon.gif")
    self.minusImage = tk.PhotoImage(file=deleteImagePath)
    saveImagePath = os.path.join(self.master.path, "resources",
                       "save_icon.gif")
    self.checkImage = tk.PhotoImage(file=saveImagePath)
    cancelImagePath = os.path.join(self.master.path, "resources",
                       "cross_icon.gif")
    self.crossImage = tk.PhotoImage(file=cancelImagePath)
    # Products
    self.productFrame = tk.Frame(self.mainFrame)
    self.productFrame.grid(sticky=tk.N+tk.W)
    # Product Name
    self.nameLabel = tk.Label(self.productFrame, text="Name: ")
    self.nameTextVar = tk.StringVar()
    self.nameTextVar.set('')
    self.nameEntry = tk.Entry(self.productFrame, textvariable=self.nameTextVar)
    self.nameLabel.grid(row=0, column=0, sticky=tk.W)
    self.nameEntry.grid(row=0, column=1, sticky=tk.W)
    # Activated
    self.activeLabel = tk.Label(self.productFrame, text="Active? ")
    self.activeState = tk.IntVar()
    self.activeState.set(1)
    self.activeCheck = tk.Checkbutton(self.productFrame, 
                       variable=self.activeState)
    self.activeLabel.grid(row=1, column=0, sticky=tk.N+tk.W)
    self.activeCheck.grid(row=1, column=1, sticky=tk.N+tk.W)
    # Brand
    self.brandLabel = tk.Label(self.productFrame, text="Brand: ")
    self.brandChoices = self.getBrandChoices()
    brandNames = [name for name,id in self.brandChoices]
    self.brandTextVar = tk.StringVar()
    self.brandTextVar.set('Choose brand...')
    self.brandMenu = tk.OptionMenu(self.productFrame, self.brandTextVar, 
                       *brandNames)
    self.brandLabel.grid(row=2, column=0, sticky=tk.N+tk.W)
    self.brandMenu.grid(row=2, column=1, sticky=tk.W+tk.N)
    # Categories
    self.categoryLabel = tk.Label(self.productFrame, text="Categories: ")
    self.categoryButton = tk.Button(self.productFrame, text="Select...",
                       command=self.openSelection)
    self.categoryList = self.getCategoryChoices()
    self.chosenCategories = []
    self.categoryText = tk.StringVar()
    self.categoryText.set('')
    self.categoryListLabel = tk.Label(self.productFrame, 
                       textvariable=self.categoryText)
    self.categoryLabel.grid(row=3, column=0, sticky=tk.N+tk.W)
    self.categoryButton.grid(row=3, column=1, sticky=tk.N+tk.W)
    self.categoryListLabel.grid(row=4, column=0, rowspan=7, columnspan=2,
                       sticky=tk.W+tk.N)
    self.categoryListLabel.config(anchor=tk.N, justify=tk.LEFT)
    # Description
    self.descLabel = tk.Label(self.productFrame, text="Description: ")
    self.descText  = tk.Text(self.productFrame, width=35, height=13)
    self.descLabel.grid(row=0, column=2, columnspan=7, sticky=tk.W)
    self.descLabel.config(justify=tk.LEFT)
    self.descText.grid(row=1, column=2, rowspan=10, columnspan=7,
                       sticky=tk.N+tk.S+tk.W)
    # Variants
    self.variantFrame = tk.Frame(self.mainFrame)
    self.variantFrame.grid(columnspan=2, sticky=tk.N+tk.W)
    self.variantTitle = tk.Label(self.variantFrame, text="VARIANTS")
    self.variants = []
    self.addVariantButton = tk.Button(self.variantFrame, image=self.plusImage,
                       text="Add Variant", compound="left",
                       command=self.addVariant)
    self.variantTitle.grid(row=12, column=0, sticky=tk.N+tk.W)
    self.addVariantButton.grid(row=13, column=0, columnspan=2, sticky=tk.N+tk.W)
    self.id = 0
    # Save
    self.saveButton = tk.Button(self.variantFrame, command=self.save,
                       text="Save", image=self.checkImage, compound="left")
    self.saveButton.grid(sticky=tk.W+tk.S)
  
  def save(self):
    """Uploads the current product to the database"""
    #TODO: save into database instead of printing
    print "Name: ", self.nameTextVar.get()
    print "IsActive: ", self.activeState.get()
    chosenBrandID = -1
    for name, id in self.brandChoices:
      if name == self.brandTextVar.get():
        chosenBrandID = id
        break
    print "Brand: ", self.brandTextVar.get(), chosenBrandID
    catNames = [name for name, id in self.chosenCategories]
    print "Categories: ", ', '.join(catNames)
    print "Description: ", self.descText.get(1.0, tk.END).strip()
    print "Variants:"
    for variant in self.variants:
      (name, price, weight) = variant.getInfo()
      print "Name: ", name, "Price: ", price, "Weight: ", weight

  def getBrandChoices(self):
    """Gets all the brands/companies with their id"""
    #TODO: retrieves from database and format correctly
    brandChoices = [("Shiseido->Elixir", 1),
                    ("L'Oreal->Maybelline", 2),
                    ("L'Oreal->Nivea", 3)]
    return brandChoices

  def getCategoryChoices(self):
    """Gets all the categories with their ids"""
    #TODO: retrieve from database and format correctly
    categoryChoices = [("Face", 0),
                       ("Face->Masks", 1),
                       ("Face->Foundation", 2),
                       ("Eye", 3),
                       ("Eye->Mascara", 4),
                       ("Skin", 5),
                       ("Skin->Foundation", 6),
                       ("Skin->Skin Care", 7)]
    return categoryChoices

  def addVariant(self):
    """Adds a new variant frame to be edited"""
    newVariant = VariantFrame(self.id, self.removeVariant(self.id),
                       self.variantFrame, self.minusImage)
    self.id += 1
    self.variants.append(newVariant)
    self.saveButton.grid_forget()
    newVariant.grid(columnspan=10)
    self.saveButton.grid(sticky=tk.W+tk.S)

  def removeVariant(self, id):
    """Returns the remove variant function when you clicked on delete"""
    def removeMe():
      """Removes the variant with a predefined id"""
      for variant in self.variants:
        if variant.id == id:
          variant.grid_forget()
          self.variants.remove(variant)
          break
    return removeMe

  def openSelection(self):
    """Opens and keeps focus on category selection window"""
    self.selectionWindow = CategorySelection(self.categorySelect,
                       self.categoryCancel, self.categoryList,
                       chosenList=self.chosenCategories,
                       selectImage=self.checkImage, cancelImage=self.crossImage)
    self.selectionWindow.title("Select categories")
    self.selectionWindow.grab_set()

  def categorySelect(self, choices):
    """Updates the chosen category list and the categoryListLabel"""
    self.chosenCategories = choices
    names = [name for name, id in choices]
    catString = '\n'.join(names)
    self.categoryText.set(catString)
    self.selectionWindow.grab_release()
    self.selectionWindow.destroy()

  def categoryCancel(self):
    """Destroys the window without updating anything"""
    self.selectionWindow.grab_release()
    self.selectionWindow.destroy()


class VariantFrame(tk.Frame):
  """A line that enables variant editing"""
  
  def __init__(self, id, deleteCommand, master=None, image=None):
    tk.Frame.__init__(self, master)
    self.id=id
    # Name
    self.nameLabel = tk.Label(self, text="Name: ")
    self.nameVar = tk.StringVar()
    self.nameEntry = tk.Entry(self, textvariable=self.nameVar)
    self.nameLabel.grid(row=0, column=0)
    self.nameEntry.grid(row=0, column=1)
    # Price
    self.priceLabel = tk.Label(self, text="Price (US$): ")
    self.priceVar = tk.StringVar()
    self.priceEntry = tk.Entry(self, textvariable=self.priceVar)
    self.priceLabel.grid(row=0, column=2)
    self.priceEntry.grid(row=0, column=3)
    # Weight
    self.weightLabel = tk.Label(self, text="Weight (g): ")
    self.weightVar = tk.StringVar()
    self.weightEntry = tk.Entry(self, textvariable=self.priceEntry)
    self.weightLabel.grid(row=0, column=4)
    self.weightEntry.grid(row=0, column=5)
    # Delete
    self.deleteButton = tk.Button(self, image=image, text="Delete",
                       compound=tk.LEFT, command=deleteCommand)
    self.deleteButton.grid(row=0, column=6)

  def getInfo(self):
    """Returns (name, price, weight)"""
    return (self.nameVar.get(), self.priceVar.get(), self.weightVar.get())


class CategorySelection(tk.Toplevel):
  """A pop-up window for selecting the categories"""
  
  def __init__(self, onSelect, onCancel, categoryList, chosenList=None,
                       selectImage=None, cancelImage=None):
    tk.Toplevel.__init__(self)
    if chosenList == None:
      chosenList = []
    self.onSelect = onSelect
    self.choices = []
    for name, id in categoryList:
      state=0
      if (name, id) in chosenList:
        state=1
      self.choices.append(CategoryChoice(id, name, state=state, master=self))
    for choice in self.choices:
      choice.grid(stick=tk.W)
    self.buttonFrame = tk.Frame(self)
    self.buttonFrame.grid()
    self.selectButton = tk.Button(self.buttonFrame, text="Select ",
                       image=selectImage, compound=tk.LEFT, command=self.select)
    self.cancelButton = tk.Button(self.buttonFrame, text="Cancel ",
                       image=cancelImage, compound=tk.LEFT, command=onCancel)
    self.selectButton.grid(row=0, column=0)
    self.cancelButton.grid(row=0, column=1)

  def select(self):
    """Callback of select button, sends selection to main widget"""
    choiceList = []
    for checkbox in self.choices:
      if checkbox.checked.get():
        choiceList.append((checkbox.name, checkbox.id))
    self.onSelect(choiceList)


class CategoryChoice(tk.Frame):
  """A label + checkbox with an idea for easy selection"""
  
  def __init__(self, id, name, state=0, master=None):
    tk.Frame.__init__(self, master)
    self.id = id
    self.name = name
    self.checked = tk.IntVar()
    self.checked.set(state)
    self.check = tk.Checkbutton(self, text=name, variable=self.checked)
    self.check.grid(sticky=tk.W)