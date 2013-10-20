import psycopg2
import json

class DBConnection(object):
  """handles connection and common requests to the database"""

  def __init__(self, dataBaseConfig):
    """dataBaseConfig: path to JSON file with db address and authentication data"""
    [self.conn, self.cur] = self.connect(dataBaseConfig)
    self.cur.execute("""SET search_path TO product_info, "$user", public;""")

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
    
  def getProductInfoByID(self, id):
    """Get the info of a product by id"""
    return self.getProductInfo(id=id)
    
  def getProductInfoByName(self, name):
    """Get the info of a product by name"""
    return self.getProductInfo(name=name)
    
  def getProductInfo(self, id=None, name=None):
    """Get the info of a product by name or by id"""
    self._checkGetProductInfoParams(id, name)
    product_info = {}
    product_info.update(self.getProductBasics(id=id, name=name))
    product_info.update(self.getProductVariants(id=id, name=name))
    product_info.update(self.getProductCategories(id=id, name=name))
    return product_info
  
  def getProductBasics(self, id=None, name=None):
    """Get the name, id, brand and company associated to name or id"""
    where = self._checkGetProductInfoParams(id, name)
    self.cur.execute(
      """
      SELECT p.product_id, b.brand_id, c.company_id
      FROM product p
      INNER JOIN brand b ON p.brand_id = b.brand_id
      INNER JOIN company c ON b.company_id = c.company_id
      WHERE {clause};
      """.format(clause=where))
    header = ("product_id", "brand_id", "company_id")
    info = self.cur.fetchone()
    return dict(zip(header, info))
    
  def getProductVariants(self, id=None, name=None):
    """Get the variants associated to the product name or id"""
    where = self._checkGetProductInfoParams(id, name)
    self.cur.execute(
      """
      SELECT p.product_id, v.variant_id
      FROM product p INNER JOIN variant v ON p.product_id = v.product_id
      WHERE {clause};
      """.format(clause=where))
    header = ("product_id", "variant_id")
    info = self.cur.fetchall()
    variants = [vid for pid, vid in info]
    return dict(zip(header, (info[0][0], variants)))
    
  def getProductCategories(self, id=None, name=None):
    """Get the categories of a product by name or by id"""
    where = self._checkGetProductInfoParams(id, name)
    self.cur.execute(
      """
      SELECT DISTINCT p.product_id, cat.category_id
      FROM product p
      INNER JOIN product_category pc ON p.product_id = pc.product_id
      INNER JOIN category cat ON cat.category_id = pc.category_id
      WHERE {clause};
      """.format(clause=where))
    header = ("product_id", "category_id")
    info = self.cur.fetchall()
    categories = [cid for pid, cid in info]
    return dict(zip(header, (info[0][0], categories)))
    
  def _checkGetProductInfoParams(self, id, name):
    """Checks the parameters and return the right condition for the query"""
    if not (id or name) or (id and name):
      raise ValueError("Need to specify either id OR name, but not both")
    if id:
      return "p.product_id = {i}".format(i=id)
    elif name:
      return "p.product_name = {n}".format(n=name)

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
  
  print "Testing DBConnection"
  import os
  path = os.path.join('..', '..', 'staging-db.json')
  db = DBConnection(path)
  print "Connected"
  print "Testing getCategoryTree"
  db.getCategoryTree(1)
  print "Category Tree: Done"
  print "Testing getProductInfo"
  print db.getProductInfo(id=3)
  print db.getProductInfo(id=1)
  print "Product Info: Done"