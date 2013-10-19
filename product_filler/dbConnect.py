import psycopg2
import json

class DBConnection(object):
  """handles connection and common requests to the database"""

  def __init__(self, dataBaseConfig):
    """dataBaseConfig: path to JSON file with db address and authentication data"""
    [self.conn, self.cur] = self.connect(dataBaseConfig)


  def connect(self, file):
    """ Connects to a database using a json file for the parameters """
    jsonFile = open(file, 'r')
    params = json.load(jsonFile)
    jsonFile.close()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    return [conn, cur]
    
  def closeConnection(self):
    """Disconnects from database"""
    self.cur.close()
    self.conn.close()

  def getCategoryTree(self, printing=0):
    """Returns a nested list representing the categories tree,
       if printing=1, prints the tree"""
    self.cur.execute(
    """SELECT cat_parent.category_id, cat.category_id
        FROM product_info.category cat
        RIGHT JOIN product_info.category cat_parent 
          ON cat.parent_id = cat_parent.category_id
        ORDER BY 1;""")
    ans = self.cur.fetchall()
    parents = set([row[0] for row in ans if row[1]])
    children = set([row[1] for row in ans if row[1]])
    root = Tree('Categories')
    nextLevel = [p for p in parents if not p in children]
    ans = [row for row in ans if row[1]]
    
    def recTreeBuild(root, children, ans):
      """Recursively find children of each node to build the Category tree"""
      if not children:
        return root
      for parentID in children:
        children = []
        newAns = ans[:]
        for i, row in enumerate(ans):
          if row[0] == parentID and row[1]:
            children.append(row[1])
            newAns.remove(row)
        ans = newAns
        parent = Tree(parentID)
        root.addChild(recTreeBuild(parent, children, ans))
      return root
    
    recTreeBuild(root, nextLevel, ans)
    if printing:
      root.printTree()
    return root

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
  
  print "Testing getCategoryTree"
  import os
  path = os.path.join('..', '..', 'staging-db.json')
  db = DBConnection(path)
  print "Connected"
  db.getCategoryTree(1)
  print "Done"