import os
import dbConnect
import Tkinter as tk
from baseWidget import BaseWidget

class ProductWidget(BaseWidget):
  """Widget for editing products"""

  def createButtons(self):
    """Creates the edition fields for the product"""
    # Product Name
    self.nameLabel = tk.Label(self.mainFrame, text="Name: ")
    self.nameTextVar = tk.StringVar()
    self.nameTextVar.set('')
    self.nameEntry = tk.Entry(self.mainFrame, textvariable=self.nameTextVar)
    self.nameLabel.grid(row=0, column=0, sticky=tk.W)
    self.nameEntry.grid(row=0, column=1, sticky=tk.W)
    # Activated
    self.activeLabel = tk.Label(self.mainFrame, text="Active? ")
    self.activeState = tk.IntVar()
    self.activeState.set(1)
    self.activeCheck = tk.Checkbutton(self.mainFrame, 
                       variable=self.activeState)
    self.activeLabel.grid(row=1, column=0, sticky=tk.N+tk.W)
    self.activeCheck.grid(row=1, column=1, sticky=tk.N+tk.W)
    # Description
    self.descLabel = tk.Label(self.mainFrame, text="Description: ")
    self.descText  = tk.Text(self.mainFrame, width=35, height=13)
    self.descLabel.grid(row=0, column=2)
    self.descText.grid(row=1, column=2, rowspan=10, columnspan=5,
                       sticky=tk.N+tk.S+tk.W+tk.E)
    # Brand
    self.brandLabel = tk.Label(self.mainFrame, text="Brand: ")
    self.brandChoices = self.getBrandChoices()
    self.brandTextVar = tk.StringVar()
    self.brandTextVar.set('')
    self.brandMenu = tk.OptionMenu(self.mainFrame, self.brandTextVar, 
                       *self.brandChoices)
    self.brandLabel.grid(row=2, column=0, sticky=tk.N+tk.W)
    self.brandMenu.grid(row=2, column=1, sticky=tk.W+tk.N)
    # Categories
    self.categoryLabel = tk.Label(self.mainFrame, text="Categories: ")
    self.categoryList = []
    self.categoryText = tk.StringVar()
    self.categoryText.set('')
    self.categoryListLabel = tk.Label(self.mainFrame, 
                       textvariable=self.categoryText)
    self.categoryLabel.grid(row=3, column=0, sticky=tk.N+tk.W)
    self.categoryListLabel.grid(row=4, column=0, rowspan=7, sticky=tk.W+tk.N)
    # Variants
    self.variantTitle = tk.Label(self.mainFrame, text="VARIANTS")
    imagePath = os.path.join(self.master.path, "resources", "plus_icon.gif")
    self.variantImage = tk.PhotoImage(file=imagePath)
    self.variants = []
    self.addVariantButton = tk.Button(self.mainFrame, image=self.variantImage,
                       text="Add Variant", compound="left",
                       command=self.addVariant)
    self.variantTitle.grid(row=12, column=0, sticky=tk.N+tk.W)
    self.addVariantButton.grid(row=13, column=0, sticky=tk.N+tk.W)
    self.nextLine = 14
    # Save
    saveImagePath = os.path.join(self.master.path, "resources",
                       "save_icon.gif")
    self.saveImage = tk.PhotoImage(file=saveImagePath)
    self.saveButton = tk.Button(self.mainFrame, text="Save", command=self.save,
                       image=self.saveImage, compound="left")
    self.saveButton.grid(sticky=tk.W+tk.S)
  
  def save(self):
    """Uploads the current product to the database"""
    #TODO: implementation
    print "Name: ", self.nameTextVar.get()
    print "IsActive: ", self.activeState.get()
    print "Brand: ", self.brandTextVar.get()
    print "Description: ", self.descText.get(1.0, tk.END).strip()

  def getBrandChoices(self):
    """Gets all the brands/companies with their id"""
    #TODO: implementation
    brandChoices = ["Shiseido->Elixir",
                    "L'Oreal->Maybelline".encode('utf-8'),
                    "L'Oreal->Nivea".encode('utf-8')]
    return brandChoices

  def getCategoryChoices(self):
    """Gets all the categories with their ids"""
    #TODO: implementation
    categoryChoices = ["Face",
                       "Face->Masks",
                       "Face->Foundation",
                       "Eye"]
    return categoryChoices

  def addVariant(self):
    """Adds a new variant frame to be edited"""
    newVariant = VariantFrame(self.mainFrame)
    self.variants.append(newVariant)
    self.saveButton.grid_forget()
    newVariant.grid(columnspan=7)
    self.saveButton.grid(sticky=tk.W+tk.S)


class VariantFrame(tk.Frame):
  """A line that enables variant editing"""
  
  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
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