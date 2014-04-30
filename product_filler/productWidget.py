import os
import sys
import dbConnect
import Tkinter as tk
import tkMessageBox
from tkFileDialog import askopenfilename
from baseWidget import BaseWidget
from imagePreview import ImagePreview
from scrolledFrame import VerticalScrolledFrame
import ImageTk

class ProductWidget(BaseWidget):
  """Widget for editing products"""

  def activate(self, db, awsManager):
    """Enables show/hide, and adds awsManager to widget"""
    self.awsManager = awsManager
    self.editionMode = 'new'
    BaseWidget.activate(self, db)

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
    self.placeholderPath = os.path.join(self.master.path, 'resources',
                       'placeholder.png')
    downImagePath = os.path.join(self.master.path, "resources", "down_icon.gif")
    self.downImage = tk.PhotoImage(file=downImagePath)
    # Load and New buttons
    self.buttonFrame = tk.Frame(self.mainFrame)
    self.buttonFrame.grid(sticky=tk.N+tk.W)
    self.newButton = tk.Button(self.buttonFrame, text="New ", command=self.new,
                       image=self.plusImage, compound=tk.LEFT)
    self.loadButton = tk.Button(self.buttonFrame, text="Load... ",
                       command=self.openProductSelection, image=self.downImage,
                       compound=tk.LEFT)
    self.newButton.grid(row=0, column=0, sticky=tk.N+tk.W)
    self.loadButton.grid(row=0, column=1, sticky=tk.N+tk.W)
    # Products
    self.productFrame = tk.Frame(self.mainFrame)
    self.productFrame.grid(columnspan=2, sticky=tk.N+tk.W)
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
                       command=self.openCategorySelection)
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
    # Pictures
    self.picturesFrame = tk.Frame(self.mainFrame)
    self.picturesFrame.grid(columnspan=3, sticky=tk.N+tk.W)
    self.prodPicLabel = tk.Label(self.picturesFrame, text="Product Picture:")
    self.prodPicButton = tk.Button(self.picturesFrame, text="Choose Image...",
                       command=self.loadProdImage)
    self.prodPicPreview = ImagePreview(size=40, master=self.picturesFrame,
                       imageFileName=self.placeholderPath)
    self.prodPicLabel.grid(row=0, column=0, sticky=tk.W)
    self.prodPicButton.grid(row=0, column=1, sticky=tk.W)
    self.prodPicPreview.grid(row=0, column=2, sticky=tk.W)
    # Variants
    self.variantFrame = tk.Frame(self.mainFrame)
    self.variantFrame.grid(columnspan=3, sticky=tk.N+tk.W)
    self.variantTitle = tk.Label(self.variantFrame, text="VARIANTS")
    self.variants = []
    self.addVariantButton = tk.Button(self.variantFrame, image=self.plusImage,
                       text="Add Variant ", compound="left",
                       command=self.addVariant)
    self.variantTitle.grid(row=12, column=0, sticky=tk.N+tk.W)
    self.addVariantButton.grid(row=13, column=0, columnspan=2, sticky=tk.N+tk.W)
    self.id = 0
    # Save
    if self.editionMode == 'new':
      self.saveButton = tk.Button(self.variantFrame, command=self.save,
                         text="Save ", image=self.checkImage, compound="left")
      self.saveButton.grid(sticky=tk.W+tk.S)
    elif self.editionMode == 'edit':
      self.saveButton = tk.Button(self.variantFrame, command=self.updateProduct,
                         text="Update ", image=self.checkImage, compound="left")
      self.saveButton.grid(sticky=tk.W+tk.S)

  def save(self):
    """Uploads the current product to the database"""
    (name, active, desc, chosenBrandID, catIds) = self.getFormInfo()
    self.checkValidity(name, chosenBrandID, catIds)
    # Save to Database, only commit after last one
    # product
    heads = ('name', 'description', 'active', 'brand_id')
    vals = (name, desc, active, chosenBrandID)
    res = self.db.simpleInsert('product', heads, vals,
                        commit=False, returning='product_id')
    self.checkDBResult(res)
    # simple insert returns the id here
    productId = res
    # product_category
    heads = ('product_id', 'category_id')
    for id in catIds:
      vals = (productId, id)
      res = self.db.simpleInsert('product_category', heads, vals, commit=False)
      self.checkDBResult(res)
    # variant
    heads = ('name', 'price', 'weight', 'product_id')
    for variant in self.variants:
      (vName, price, weight) = variant.getInfo()
      vals = (vName, int(price), int(weight), productId)
      res = self.db.simpleInsert('variant', heads, vals, commit=False)
      self.checkDBResult(res)
    # Finally commit
    self.db.conn.commit()
    # Upload Images to S3
    success = True
    prodImgFileName = self.prodPicPreview.getImageFileName()
    if prodImgFileName != self.placeholderPath:
      keyName = self.awsManager.createKey(productId, name)
      metadata = {'alt':'picture of ' + str(name),
                  'title':name}
      try:
        self.awsManager.uploadImage(keyName, prodImgFileName, **metadata)
      except Exception, e:
        success = False
        print 'Error while uploading product image: ', prodImgFileName
        print e
    variantsData = self.db.getProductVariants(id=productId)
    variantIds = sorted(variantsData['variant_ids'])
    for i, variant in enumerate(self.variants):
      variantImgPath = variant.getImagePath()
      if variantImgPath != self.placeholderPath:
        # using the fact that they were added in the same order
        variantId = variantIds[i]
        variantName = variant.getInfo()[0]
        variantKey = self.awsManager.createKey(productId, name,
                       variantId, variantName)
        metadata = {'alt':'picture of {} from {}'.format(variantName, name),
                    'title':'{} from {}'.format(variantName, name)}
        try:
          self.awsManager.uploadImage(variantKey, variantImgPath, **metadata)
        except Exception, e:
          success = False
          print 'Error while uploading variant image: ', variantImgPath
          print e
    self.productSelect(productId)
    if success:
      tkMessageBox.showinfo('Product Upload Success',
                       'The product was saved in\n'
                       'in the database successfully.\n'
                       'You are now in Update mode.\n'
                       'Click "New" to start a new product.')
    else:
      tkMessageBox.showwarning('Product Upload Half-Succes',
                         'The product was saved in the database.\n'
                         'Sorry: not all images could be uploaded.\n'
                         'You are now in Update mode.\n'
                         'Click "New" to start a new product.')

  def updateProduct(self):
    """Updates a product that is already in the database"""
    (name, active, desc, chosenBrandID, catIds) = self.getFormInfo()
    self.checkValidity(name, chosenBrandID, catIds)
    productId = self.currentProduct['product_id']
    # Update into Database, only commit after last one
    # product
    heads = ('name', 'description', 'active', 'brand_id')
    vals = (name, desc, active, chosenBrandID)
    res = self.db.simpleUpdate('product', heads, vals, productId, commit=False)
    self.checkDBResult(res)
    # product_category
    # First delete relations that disappeared
    for id in self.currentProduct['category_ids']:
      if id not in catIds:
        res = self.db.deleteProductCategoryLine(productId, id, commit=False)
        self.checkDBResult(res)
    # Then add any new category relationship
    heads = ('product_id', 'category_id')
    for id in catIds:
      if id not in self.currentProduct['category_ids']:
        vals = (productId, id)
        res = self.db.simpleInsert('product_category', heads, vals, commit=False)
        self.checkDBResult(res)
    # variant
    # First delete any variant that was deleted
    variantIds = [variant.variantId for variant in self.variants]
    for id in self.currentProduct['variant_ids']:
      if id not in variantIds:
        res = self.db.deleteLineFromId('variant', id)
        self.checkDBResult(res)
    # Then insert/update the variants from the form
    heads = ('name', 'price', 'weight', 'product_id')
    for variant in self.variants:
      (vName, price, weight) = variant.getInfo()
      vals = (vName, int(price), int(weight), productId)
      if variant.variantId:
        res = self.db.simpleUpdate('variant', heads, vals, variant.variantId,
                       commit=False)
      else:
        res = self.db.simpleInsert('variant', heads, vals, commit=False)
      self.checkDBResult(res)
    # Finally commit
    self.db.conn.commit()

    # Upload Images to S3
    oldName = self.currentProduct['product_name']
    oldKey = self.awsManager.createKey(productId, oldName)
    newKey = None
    newMetadata = None
    newImage = None
    if name != oldName:
      newMetadata = {'alt':'picture of ' + str(name),
                     'title':name}
      newKey = self.awsManager.createKey(productId, name)
    if self.imageModified:
      newImage = self.prodPicPreview.getImageFileName()
    self.awsManager.updateImage(oldKey, newName=newKey,
                       newMetadata=newMetadata, newImagePath=newImage)
    # delete unused variant images
    for id in self.currentProduct['variant_ids']:
      if id not in variantIds:
        oldName = self.currentProduct['product_name']
        oldVariantName = self.currentProduct['variants'][id]['variant_name']
        vKey = self.awsManager.createKey(productId, oldName, id,
                       oldVariantName)
        self.awsManager.deleteKey(vKey)
    # update images for all the other keys
    variantsInfo = self.db.getProductVariants(id=productId)
    for variant in self.variants:
      # always update if current image is different from placeholder
      vImgPath = variant.getImagePath()
      if vImgPath != self.placeholderPath:
        vName = variant.getInfo()[0]
        vId = variant.variantId
        newKey = self.awsManager.createKey(productId, name, vId, vName)
        metadata = {'alt':'picture of {} from {}'.format(vName, name),
                    'title':'{} from {}'.format(vName, name)}
        if variant.variantId:
          # update case
          oldName = self.currentProduct['product_name']
          oldVName = self.currentProduct['variants'][vId]['variant_name']
          oldKey = self.awsManager.createKey(productId, oldName, vId, oldVName)
          self.awsManager.updateImage(oldKey, newName=newKey,
                       newMetadata=metadata, newImagePath=vImgPath)
        else:
          # create case: need to find id first
          for key, val in variantsInfo['variants'].items():
            if variant.getInfo() == (val['variant_name'],
                       str(val['variant_price']), str(val['variant_weight'])):
              vId = key
              break
          newKey = self.awsManager.createKey(productId, name, vId, vName)
          self.awsManager.uploadImage(newKey, vImgPath, **metadata)

    # Reloading Product info in Widget
    self.productSelect(productId)
    tkMessageBox.showinfo('Product Update Success',
                       'The product was updated in\n'
                       'in the database successfully.\n'
                       'You are now in Update mode.\n')

  def getFormInfo(self):
    """Retrieves all the information from the different entries and checkboxes"""
    name = self.nameTextVar.get().encode('utf-8').strip()
    active = self.activeState.get() == 1
    desc = self.descText.get(1.0, tk.END).encode('utf-8').strip()
    chosenBrandID = -1
    brandText = self.brandTextVar.get().encode('utf-8')
    for brandName, id in self.brandChoices:
      if brandName == brandText:
        chosenBrandID = id
        break
    catIds = [id for _, id in self.chosenCategories]
    return (name, active, desc, chosenBrandID, catIds)

  def checkValidity(self, name, chosenBrandID, catIds):
    """Checks if all the inputs are filled/valid"""
    if not name:
      errorText = "Name cannot be blank"
      tkMessageBox.showerror('ProductWidgetError', errorText)
      raise ProductWidgetError(errorText)
    elif chosenBrandID == -1:
      errorText = "Product must have a brand"
      tkMessageBox.showerror('ProductWidgetError', errorText)
      raise ProductWidgetError(errorText)
    elif not catIds:
      errorText = "Product must have at least one category"
      tkMessageBox.showerror('ProductWidgetError', errorText)
      raise ProductWidgetError(errorText)
    elif not (self.variants and self.variants[0]):
      if not tkMessageBox.askokcancel("Confirm Product update/save",
          "Product has no variant\nConfirm for save/update"):
        raise ProductWidgetError("Creation cancelled by user")
    for variant in self.variants:
      (vName, price, weight) = variant.getInfo()
      if not (vName and price):
        errorText = "All variants need a name and price"
        tkMessageBox.showerror('ProductWidgetError', errorText)
        raise ProductWidgetError(errorText)
      try:
        int(price)
        int(weight)
      except ValueError:
        errorText = "Variant price and weight must be int"
        tkMessageBox.showerror('ProductWidgetError', errorText)
        raise ProductWidgetError(errorText)

  def getBrandChoices(self):
    """Gets all the brands/companies with their id"""
    brandTree = self.db.getBrandTree()
    brandChoices = []
    for company in brandTree.leaves:
      for brand in company.leaves:
        brandChoices.append((company.cargo['name']+'->'+brand.cargo['name'],
                       brand.cargo['id']))
    return brandChoices

  def getCategoryChoices(self):
    """Gets all the categories with their ids"""
    categoryTree = self.db.getCategoryTree()
    categoryChoices = []
    for cat in categoryTree.leaves:
      categoryChoices += self.recursiveCategoryNames(cat)
    return categoryChoices

  def recursiveCategoryNames(self, tree, prefix=''):
    """Recursively builds the names of all the categories"""
    if prefix:
      name = prefix + '->' + tree.cargo['name']
    else:
      name = tree.cargo['name']
    newLine = (name, tree.cargo['id'])
    children = []
    for leaf in tree.leaves:
      children += self.recursiveCategoryNames(leaf, name)
    return [newLine] + children

  def addVariant(self, variantData=None):
    """Adds a new variant frame to be edited"""
    newVariant = VariantFrame(self.id, self.removeVariant(self.id),
                       self.variantFrame, deleteImage=self.minusImage,
                       imagePath=self.placeholderPath)
    self.variants.append(newVariant)
    if variantData:
      id, info = variantData
      newVariant.set(id=id, name=info['variant_name'],
                       weight=str(info['variant_weight']),
                       price=str(info['variant_price']))
      variantKey = self.awsManager.createKey(self.currentProduct['product_id'],
                       self.currentProduct['product_name'],
                       id, info['variant_name'])
      destFile = os.path.join(os.getenv('LOCALAPPDATA'), 'cosmexo',
                       'variant_{}.jpg'.format(self.id))
      if self.awsManager.getImageFromName(variantKey, destFile):
        newVariant.setImagePath(destFile)
    self.id += 1
    # Place variant before save button
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

  def openCategorySelection(self):
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

  def loadProdImage(self):
    """Loads the product image into the ImagePreview widget"""
    self.imageModified = True
    path = self.master.config.get(u'last_img_file_path') or \
           os.path.abspath(os.path.dirname(sys.argv[0]))
    imgFile = askopenfilename(initialdir=path)
    if imgFile is '':
      return
    self.master.config.set(u'last_img_file_path',
                           os.path.abspath(os.path.dirname(imgFile)))
    self.prodPicPreview.setImageFromFileName(imgFile)

  def new(self):
    """All texts become blank, and saving will create a new product in db"""
    title = "New Product"
    message = "Starting a new product will\nerase unsaved modifications"
    if tkMessageBox.askokcancel(title, message, icon=tkMessageBox.WARNING):
      self.editionMode = 'new'
      self.clearAllInfo()

  def openProductSelection(self):
    """Opens product choosing window"""
    title = "New Product"
    message = "Loading a product will\nerase unsaved modifications"
    if tkMessageBox.askokcancel(title, message, icon=tkMessageBox.WARNING):
      productList = self.db.getAllProductsWithBrands()
      self.productSelection = ProductSelection(self.productSelect,
                         self.productCancel, productList,
                         selectImage=self.downImage, cancelImage=self.crossImage)
      self.productSelection.title("Product Selection")
      self.productSelection.grab_set()

  def productSelect(self, productID):
    """Gets all the product info and pre-fills all the entries"""
    productInfo = self.db.getProductInfoByID(productID)
    self.currentProduct = productInfo
    self.editionMode = 'edit'
    self.imageModified = False
    self.clearAllInfo()
    self.nameTextVar.set(productInfo['product_name'])
    self.activeState.set(productInfo['product_active'])
    for name, id in self.brandChoices:
      if id==productInfo['brand_id']:
        self.brandTextVar.set(name)
        break
    for name, id in self.categoryList:
      if id in productInfo['category_ids']:
        self.chosenCategories.append((name, id))
    catNames = [name for name, id in self.chosenCategories]
    self.categoryText.set('\n'.join(catNames))
    self.descText.insert(1.0, productInfo['product_description'])
    #images
    keyName = self.awsManager.createKey(productID, productInfo['product_name'])
    prodImgPath = os.path.join(os.getenv('LOCALAPPDATA'), 'cosmexo',
                       'product.jpg')
    if self.awsManager.getImageFromName(keyName, prodImgPath):
      self.prodPicPreview.setImageFromFileName(prodImgPath)
    for variantData in productInfo['variants'].items():
      self.addVariant(variantData=variantData)

  def productCancel(self):
    """Removes the product selection pop-up"""
    self.productSelection.grab_release()
    self.productSelection.destroy()

  def clearAllInfo(self):
    """Clears the info about the current product"""
    for variant in self.variants:
        self.removeVariant(variant.id)()
    self.updateMainFrame()
    self.id = 0

  def checkDBResult(self, res):
    """Checks if DBConnect succeeded, throws error and roll back if not"""
    if isinstance(res, Exception):
      self.db.conn.rollback()
      tkMessageBox.showerror('ProductWidgetError', res)
      raise res


class VariantFrame(tk.Frame):
  """A line that enables variant editing"""

  def __init__(self, id, deleteCommand, master=None, deleteImage=None,
                       imagePath=None):
    tk.Frame.__init__(self, master)
    self.id=id
    self.variantId = None
    self.imageModified = False
    # Name
    self.nameLabel = tk.Label(self, text="Name: ")
    self.nameVar = tk.StringVar()
    self.nameEntry = tk.Entry(self, textvariable=self.nameVar)
    self.nameLabel.grid(row=0, column=0)
    self.nameEntry.grid(row=0, column=1)
    # Price
    self.priceLabel = tk.Label(self, text="Price (US$): ")
    self.priceVar = tk.StringVar()
    self.priceEntry = tk.Entry(self, textvariable=self.priceVar, width=8)
    self.priceLabel.grid(row=0, column=2)
    self.priceEntry.grid(row=0, column=3)
    # Weight
    self.weightLabel = tk.Label(self, text="Weight (g): ")
    self.weightVar = tk.StringVar()
    self.weightEntry = tk.Entry(self, textvariable=self.weightVar, width=8)
    self.weightLabel.grid(row=0, column=4)
    self.weightEntry.grid(row=0, column=5)
    # Image preview
    self.picButton = tk.Button(self, text="Choose Image...",
                       command=self.loadImage)
    self.imagePreview = ImagePreview(size=40, master=self,
                       imageFileName=imagePath)
    self.picButton.grid(row=0, column=6)
    self.imagePreview.grid(row=0, column=7)
    # Delete
    self.deleteButton = tk.Button(self, image=deleteImage, text="Delete",
                       compound=tk.LEFT, command=deleteCommand)
    self.deleteButton.grid(row=0, column=8)

  def getInfo(self):
    """Returns (name, price, weight)"""
    return (self.nameVar.get().encode('utf-8').strip(), self.priceVar.get(),
                       self.weightVar.get())

  def set(self, name='', price='', weight='', id=None):
    """sets the entries to a specific value"""
    self.nameVar.set(name)
    self.priceVar.set(price)
    self.weightVar.set(weight)
    self.variantId = id

  def loadImage(self):
    """Loads the product image into the ImagePreview widget"""
    parent = self.nametowidget('.root')
    path = parent.config.get(u'last_img_file_path') or \
           os.path.abspath(os.path.dirname(sys.argv[0]))
    imgFile = askopenfilename(initialdir=path)
    if imgFile is '':
      return
    parent.config.set(u'last_img_file_path',
                           os.path.abspath(os.path.dirname(imgFile)))
    self.imagePreview.setImageFromFileName(imgFile)
    self.imageModified = True

  def getImagePath(self):
    """Returns path of variant image"""
    return self.imagePreview.getImageFileName()

  def setImagePath(self, path):
    """Sets the image path"""
    self.imagePreview.setImageFromFileName(path)


class CategorySelection(tk.Toplevel):
  """A pop-up window for selecting the categories"""

  def __init__(self, onSelect, onCancel, categoryList, chosenList=None,
                       selectImage=None, cancelImage=None):
    tk.Toplevel.__init__(self)
    self.choicesFrame = VerticalScrolledFrame(self)
    if chosenList == None:
      chosenList = []
    self.onSelect = onSelect
    self.choices = []
    for name, id in categoryList:
      state=0
      if (name, id) in chosenList:
        state=1
      self.choices.append(CategoryChoice(id, name, state=state,
                       master=self.choicesFrame.interior))
    for choice in self.choices:
      choice.grid(stick=tk.W)
    self.choicesFrame.grid()
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


class ProductSelection(tk.Toplevel):
  """A pop-up window that allows to select a product to edit"""

  def __init__(self, onSelect, onCancel, productList, selectImage=None,
                       cancelImage=None):
    tk.Toplevel.__init__(self)
    self.onSelect = onSelect
    self.selection = tk.IntVar()
    self.selection.set(-1)
    self.productListFrame = VerticalScrolledFrame(self)
    for p in productList:
      t = ', '.join(p[1:])
      button = tk.Radiobutton(self.productListFrame.interior, text=t,
                       variable=self.selection, value=p[0], indicatoron=0)
      button.grid(sticky=tk.N+tk.W)
    self.productListFrame.grid()
    self.buttonFrame = tk.Frame(self)
    self.buttonFrame.grid()
    self.selectButton = tk.Button(self.buttonFrame, text="Select ",
                       image=selectImage, compound=tk.LEFT, command=self.select)
    self.cancelButton = tk.Button(self.buttonFrame, text="Cancel ",
                       image=cancelImage, compound=tk.LEFT, command=onCancel)
    self.selectButton.grid(row=0, column=0)
    self.cancelButton.grid(row=0, column=1)

  def select(self):
    """Callback of select button, calls ProductWidget method with product id"""
    if self.selection.get() == -1:
      message = 'You need to select\nat least one product'
      tkMessageBox.showerror('Product Choice Error', message)
    else:
      self.onSelect(self.selection.get())
      self.grab_release()
      self.destroy()


class ProductWidgetError(BaseException):
  """Error raised when trying to save/update a product"""

  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)