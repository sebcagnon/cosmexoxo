import Tkinter as tk

class TextEditFrame(tk.Frame):
  """A frame for creating a new category"""

  def __init__(self, master=None, textVar=None, labelText='',
                buttonText='', buttonAction=None, cancelButtonAction=None):
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
    if not buttonAction:
      raise ValueError("No action linked to main button in TextEditFrame")
    def entryAction(event):
      """Ditch the event, call buttonAction"""
      buttonAction()
    self.entry.bind("<Return>", entryAction)
    # Buttons
    self.addButton = tk.Button(self, text=buttonText,
        command=buttonAction)
    self.addButton.grid(row=2, column=0)
    self.cancelButton = tk.Button(self, text='Cancel',
        command=cancelButtonAction)
    self.cancelButton.grid(row=2, column=1)