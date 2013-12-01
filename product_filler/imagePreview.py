import Tkinter as tk
import ImageTk

class ImagePreview(tk.Label):
  """A class for displaying small previews of an image and the full size on
     mouse over"""
  
  def __init__(self, size, imageFileName=None, master=None):
    """size in pixel of the squared preview"""
    tk.Label.__init__(self, master)
    self.size = [size, size]
    if imageFileName:
      self.setImageFromFileName(imageFileName)

  def setImageFromFileName(self, fileName):
    """Opens the image from file name, creates the preview, and displays"""
    self.fileName = fileName
    self.image = ImageTk.Image.open(fileName)
    self.photo = ImageTk.PhotoImage(self.image)
    self.previewImage = self.image.copy()
    self.previewImage.thumbnail(self.size, ImageTk.Image.ANTIALIAS)
    self.previewPhoto = ImageTk.PhotoImage(self.previewImage)
    self.configure(image=self.previewPhoto)