class Tree(object):
  """A simple Tree class"""

  def __init__(self, cargo, leaves=None):
    """cargo is the information of the node, leaves is the list of leaves"""
    self.cargo = cargo
    if leaves is None:
      self.leaves = []
    else:
      self.leaves = leaves

  def __str__(self):
    return str(self.cargo)

  def addChild(self, node):
    """Adds node to the list of children"""
    self.leaves.append(node)

  def printTree(self, tab=0):
    """Prints the tree with nice tabulation"""
    print '\t'*tab + str(self.cargo)
    if self.leaves:
      for child in self.leaves:
        child.printTree(tab+1)

if __name__=='__main__':
  #Testing the Tree class
  print "Printing nice tree:"
  leaf3 = Tree(3)
  leaf2 = Tree(2)
  leaf2.addChild(leaf3)
  leaf1 = Tree(1)
  root = Tree(0, [leaf2, leaf1])
  root.printTree()
  print