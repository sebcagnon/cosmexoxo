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

  # PRODUCT INFO FOR PRODUCT PAGE
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

  # CATEGORIES
  def getCategoryTree(self, printing=0):
    """Returns a nested dict representing the categories tree,
       if printing=1, prints the tree"""
    self.cur.execute(
    """SELECT cat_parent.category_id, cat_parent.name, cat.category_id
        FROM product_info.category cat
        RIGHT JOIN product_info.category cat_parent
          ON cat.parent_id = cat_parent.category_id
        ORDER BY 1;""")
    ans = self.cur.fetchall()
    flatTree = {id:{'id':id, 'name':name} for id, name, _ in ans}
    children = set([row[-1] for row in ans if row[-1]])
    roots = set([row[0] for row in ans if row[0] not in children])
    root = tree.Tree({'name':'Categories','id':-1})
    nextLevel = list(roots)
    ans = [row for row in ans if row[-1]]
    self.recTreeBuild(root, nextLevel, ans, flatTree)
    if printing:
      root.printTree()
    return root

  def deleteCategory(self, id):
    """Delete the category using its id"""
    try:
      self.cur.execute(
        """DELETE FROM category
        WHERE category.category_id = {id}
        """.format(id=id))
      self.conn.commit()
      return True
    except psycopg2.Error, e:
      return e

  def addCategory(self, name, parentID):
    """Add a new category child of company with the parentID.
       Use parentID=-1 for root category"""
    if not name:
      return ValueError('addCategory: name cannot be empty')
    if parentID==-1:
      parent_id = 'NULL'
    else:
      parent_id = parentID
    try:
      self.cur.execute(
        """INSERT INTO category (name, parent_id)
        VALUES ('{cat_name}', {pid})
        """.format(cat_name=name, pid=parent_id))
      self.conn.commit()
      return True
    except psycopg2.Error, e:
      return e

  def editCategory(self, name, id):
    """Edit the name of the category identified by id"""
    if not name:
      return ValueError('editCategory: name cannot be empty')
    try:
      self.cur.execute(
        """UPDATE category
        SET name='{cat_name}' WHERE category_id={cid}
        """.format(cat_name=name, cid=id))
      self.conn.commit()
      return True
    except psycopg2.Error, e:
      return e
  
  def recTreeBuild(self, root, children, ans, treeElements):
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
      parent = tree.Tree(treeElements[parentID])
      root.addChild(self.recTreeBuild(parent, children, ans, treeElements))
    return root

  # COMPANIES/BRANDS
  def getBrandTree(self, printing=0):
    """Returns a nested dict representing the companies and their brands,
       if printing=1, prints the tree"""
    self.cur.execute(
    """SELECT c.company_id, c.name, c.in_navbar,
        b.brand_id, b.name, b.in_navbar
        FROM company c
        LEFT JOIN brand b ON b.company_id = c.company_id
        ORDER BY c.company_id;""")
    ans = self.cur.fetchall()
    root = tree.Tree({'name':'Companies', 'id':-1, 'in_navbar':False})
    currentCompany = None
    for line in ans:
      if currentCompany == None or line[0] != currentCompany.cargo['id']:
        currentCompany = tree.Tree({'id':line[0],
                                    'name':line[1],
                                    'in_navbar':line[2]})
        root.addChild(currentCompany)
      currentCompany.addChild(tree.Tree({'id':line[3],
                                         'name':line[4],
                                         'in_navbar':line[5]}))
    if printing:
      root.printTree()
    return root

  def editLineFromId(self, table, column, newValue, id):
    """UPDATE table SET column=newValue WHERE 'table'_id=id"""
    val = self.formatValue(newValue)
    try:
      self.cur.execute(
        """UPDATE {table}
           SET {column}={value} WHERE {table}_id={id}
        """.format(table=table, column=column, value=val, id=id))
      self.conn.commit()
      return True
    except psycopg2.Error, e:
      return e
  
  def formatValue(self, value):
    """Format values for compatibility with database queries"""
    if value is True:
      return 'TRUE'
    elif value is False:
      return 'FALSE'
    elif isinstance(value, (int, float, long)):
      return value
    elif isinstance(value, str):
      return repr(value)
    else:
      return value

if __name__=='__main__':
  print "Testing DBConnection"
  import os
  path = os.path.join('..', '..', 'staging-db.json')
  db = DBConnection(path)
  print "Connected"
  print "Testing getCategoryTree"
  db.getCategoryTree(1)
  print "Category Tree: Done"
  print "Testing getBrandTree"
  db.getBrandTree(1)
  print "Brand Tree: Done"
  print "Testing getProductInfo"
  print db.getProductInfo(id=7)
  print db.getProductInfo(id=8)
  print "Product Info: Done"