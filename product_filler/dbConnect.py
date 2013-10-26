import psycopg2
import json
import tree

class DBConnection(object):
  """handles connection and common requests to the database"""

  def __init__(self, dataBaseConfig):
    """dataBaseConfig: path to JSON file with db address and authentication data"""
    self.connect(dataBaseConfig)
    self.cur.execute("""SET search_path TO product_info, "$user", public;""")

  def connect(self, file):
    """ Connects to a database using a json file for the parameters """
    jsonFile = open(file, 'r')
    params = json.load(jsonFile)
    jsonFile.close()
    self.conn = psycopg2.connect(**params)
    self.cur = self.conn.cursor()

  def closeConnection(self):
    """Disconnects from database"""
    self.cur.close()
    self.conn.close()

  def getCategoryTree(self, printing=0):
    """Returns a nested list representing the categories tree,
       if printing=1, prints the tree"""
    self.cur.execute(
    """SELECT cat_parent.category_id, cat_parent.name, cat.category_id
        FROM product_info.category cat
        RIGHT JOIN product_info.category cat_parent
          ON cat.parent_id = cat_parent.category_id
        ORDER BY 1;""")
    ans = self.cur.fetchall()
    flatTree = {id:{'id':id, 'name':name} for id, name, _ in ans}
    parents = set([row[0] for row in ans if row[-1]])
    children = set([row[1] for row in ans if row[-1]])
    root = tree.Tree({'name':'Categories','id':-1})
    nextLevel = [p for p in parents if not p in children]
    ans = [row for row in ans if row[-1]]

    def recTreeBuild(root, children, ans):
      """Recursively find children of each node to build the Category tree"""
      if not children:
        return root
      for parentID in children:
        children = []
        newAns = ans[:]
        for i, row in enumerate(ans):
          if row[0] == parentID and row[-1]:
            children.append(row[-1])
            newAns.remove(row)
        ans = newAns
        parent = tree.Tree(flatTree[parentID])
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
      SELECT p.product_id, p.name, p.description, p.active,
      b.brand_id, b.name, c.company_id, c.name
      FROM product p
      INNER JOIN brand b ON p.brand_id = b.brand_id
      INNER JOIN company c ON b.company_id = c.company_id
      WHERE {clause};
      """.format(clause=where))
    header = ("product_id", "product_name", "product_description", 
              "product_active", "brand_id", "brand_name",
              "company_id", "company_name")
    info = self.cur.fetchone()
    if info:
      return dict(zip(header, info))
    else:
      return {}

  def getProductVariants(self, id=None, name=None):
    """Get the variants associated to the product name or id"""
    where = self._checkGetProductInfoParams(id, name)
    self.cur.execute(
      """
      SELECT p.product_id, v.variant_id, v.name, v.price, v.weight
      FROM product p INNER JOIN variant v ON p.product_id = v.product_id
      WHERE {clause};
      """.format(clause=where))
    header = ("variant_name", "variant_price", "variant_weight")
    info = self.cur.fetchall()
    if info:
      vids = [row[1] for row in info]
      res = {"product_id":info[0][0], "variant_ids":vids}
      variants = {}
      for row in info:
        variants[row[1]] = dict(zip(header, row[2:]))
      res["variants"] = variants
      return res
    else:
      return {}

  def getProductCategories(self, id=None, name=None):
    """Get the categories of a product by name or by id"""
    where = self._checkGetProductInfoParams(id, name)
    self.cur.execute(
      """
      SELECT DISTINCT p.product_id, cat.category_id, cat.name
      FROM product p
      INNER JOIN product_category pc ON p.product_id = pc.product_id
      INNER JOIN category cat ON cat.category_id = pc.category_id
      WHERE {clause};
      """.format(clause=where))
    info = self.cur.fetchall()
    if info:
      cids = [row[1] for row in info]
      res = {"product_id":info[0][0], "category_ids":cids}
      categories = {}
      for row in info:
        categories[row[1]] = {"category_name":row[2]}
      res["categories"] = categories
      return res
    else:
      return {}

  def _checkGetProductInfoParams(self, id, name):
    """Checks the parameters and return the right condition for the query"""
    if not (id or name) or (id and name):
      raise ValueError("Need to specify either id OR name, but not both")
    if id:
      return "p.product_id = {i}".format(i=id)
    elif name:
      return "p.product_name = {n}".format(n=name)


if __name__=='__main__':
  print "Testing DBConnection"
  import os
  path = os.path.join('..', '..', 'staging-db.json')
  db = DBConnection(path)
  print "Connected"
  print "Testing getCategoryTree"
  db.getCategoryTree(1)
  print "Category Tree: Done"
  print "Testing getProductInfo"
  print db.getProductInfo(id=7)
  print db.getProductInfo(id=8)
  print "Product Info: Done"