var pg = require('pg');
var fs = require('fs');
var async = require('async');
var _ = require('underscore');

// initializing db values

var PGPASS_FILE = './.pgpass';
if (process.env.DATABASE_URL) {
  var pgregex = /postgres:\/\/([^:]+):([^@]+)@([^:]+):(\d+)\/(.+)/;
  var match = process.env.DATABASE_URL.match(pgregex);
  var user = match[1];
  var password = match[2];
  var host = match[3];
  var port = match[4];
  var dbname = match[5];
} else {
  var pgtokens = fs.readFileSync(PGPASS_FILE).toString().split(':');
  var host = pgtokens[0];
  var port = pgtokens[1];
  var dbname = pgtokens[2];
  var user = pgtokens[3];
  var password = pgtokens[4];
}

var config = {
  user: user,
  password: password,
  database: dbname,
  host: host,
  port: port,
  ssl: true
};

var db = {

  // Get product info from db and format it into a nice Product object
  getProduct : function (productId, callback) {
    async.parallel([
        async.apply(getProductBasics, productId),
        async.apply(getProductCategories, productId),
        async.apply(getProductVariants, productId)
      ],
      function(err, result) {
        if (err) return callback(err);
        var product = createProduct(result)
        callback(null, product);
      })
  },

  // Returns a list of all products as the pair {product_id, name}
  getProductsList : function (callback) {
    pg.connect(config, function onConnected(err, client, done) {
      if (err) return callback(err);
      var str = 'SELECT product_id, name FROM product_info.product';
      client.query(str, function onQueryFinished(err, result) {
        if (err) {
          callback(err);
        } else {
          callback(null, result.rows);
        }
        done();
      });
    });
  },

  // Returns a list of all products from 1 brand as the pair {product_id, name}
  getProductsByBrand : function (brandName, callback) {
    pg.connect(config, function prodByBrandQuery(err, client, done) {
      if (err) return callback(err);
      var str = 'SELECT p.product_id, p.name, p.description as desc\
                 FROM product_info.product p\
                 LEFT JOIN product_info.brand b ON p.brand_id = b.brand_id\
                 WHERE b.name = $1';
      client.query(str, [brandName], function onQueryFinished(err, result) {
        if (err) {
          callback(err);
        } else {
          callback(null, _.map(result.rows, function addKeys (row) {
            row.key = db.createKey([row.product_id, row.name]);
            row.link = '/product/' + row.product_id;
            return row;
          }));
        }
        done();
      });
    });
  },

  // returns list of all companies with their respective brands
  // also give their IDs and whether they are active
  getAllBrands : function (callback) {
    brandsRequest(callback);
  },

  // same as getAllBrands, but filters to only keep in_navbar ones
  getNavbarBrands : function (callback) {
    brandsRequest(function onBrands(err, brandTree) {
      if (err) return callback(err);
      var filteredTree = filterBrands(brandTree);
      callback(null, filteredTree);
    });
  },

  // gets all categories and returns them as a nice tree structure
  getAllCategories : function (callback) {
    categoriesRequest(callback);
  },

  getProductsByCategory : function (categoryName, callback) {
    pg.connect(config, function prodByCatQuery(err, client, done) {
      if (err) return callback(err);
      var str = 'SELECT p.product_id, p.name, p.description as desc\
                 FROM product_info.product p\
                 INNER JOIN product_info.product_category pc\
                  ON p.product_id = pc.product_id\
                 INNER JOIN product_info.category c\
                  ON pc.category_id = c.category_id\
                 WHERE c.name = $1';
      client.query(str, [categoryName], function onQueryFinished(err, result) {
        if (err) {
          callback(err);
        } else {
          callback(null, _.map(result.rows, function addKeys (row) {
            row.key = db.createKey([row.product_id, row.name]);
            row.link = '/product/' + row.product_id;
            return row;
          }));
        }
        done();
      });
    });
  },

  // finds a category in the tree by name, and returns the subtree
  findSubTree : function (name, tree) {
    for (var i=0; i<tree.length; i++) {
      if (tree[i].name == name) {
        return tree[i];
      } else {
        var sub = db.findSubTree(name, tree[i].children);
        if (sub != undefined) return sub;
      }
    }
    return;
  },

  // Closes remaining connections to the database
  // after queries have all returned
  // to allow for programs to finish nicely.
  close : function () {
    pg.end();
  },

  // Creates an key for AWS S3 from products/variants name and id
  createKey : function (keyParts) {
    var key = keyParts.join('_');
    return replaceAll(' ', '-', key)
           .replace(/[!"#$%&'()\*\+,\.\/:;\<=\>\?@\[\\\]\^`\{\|\}~]/g, '');
  }

}; // end of exported functions


// query functions meant to be used in async

// Fetch basic info directly available from the Product table
function getProductBasics(productId, callback) {
  pg.connect(config, function onConnected(err, client, done) {
    if (err) return callback(err);
    var str = "SELECT p.product_id, p.name, p.description, p.active,\
      b.brand_id, b.name as brand_name, c.company_id,\
      c.name as company_name\
      FROM SCHEMA.product p\
      INNER JOIN SCHEMA.brand b ON p.brand_id = b.brand_id\
      INNER JOIN SCHEMA.company c ON b.company_id = c.company_id\
      WHERE p.product_id = $1";
    var newStr = replaceAll('SCHEMA', 'product_info', str);
    client.query(newStr, [productId], function onQueryFinished(err, result) {
      callback(err, result.rows);
      done();
    });
  });
}

// Fetch list of categories associated with the Product
function getProductCategories(productId, callback) {
  pg.connect(config, function onConnected(err, client, done) {
    if (err) return callback(err);
    var str = "SELECT DISTINCT p.product_id, cat.category_id, cat.name\
      FROM SCHEMA.product p\
      INNER JOIN SCHEMA.product_category pc ON p.product_id = pc.product_id\
      INNER JOIN SCHEMA.category cat ON cat.category_id = pc.category_id\
      WHERE p.product_id = $1"
    var newStr = replaceAll('SCHEMA', 'product_info', str);
    client.query(newStr, [productId], function onQueryFinished(err, result) {
      callback(err, result.rows);
      done();
    });
  });
}

// Fetch list of variants associated with the Product
function getProductVariants(productId, callback) {
  pg.connect(config, function onConnected(err, client, done) {
    if (err) return callback(err);
    var str = "SELECT p.product_id, v.variant_id, v.name, v.price, v.weight\
      FROM SCHEMA.product p\
      INNER JOIN SCHEMA.variant v ON p.product_id = v.product_id\
      WHERE p.product_id = $1";
    var newStr = replaceAll('SCHEMA', 'product_info', str);
    client.query(newStr, [productId], function onQueryFinished(err, result) {
      callback(err, result.rows);
      done();
    });
  });
}

// Creates a nice Product object to use in webpage from async result
function createProduct(result) {
  var basics = result[0][0];
  var product = {
    product_id: basics.product_id,
    name: basics.name,
    desc: basics.description,
    key: db.createKey([basics.product_id, basics.name]),
    brand_name: basics.brand_name,
    company_name: basics.company_name,
    link: '/product/' + basics.product_id,
    categories: _.pluck(result[1], 'name'),
    variants: _.map(result[2], function selector(variant) {
                return {variant_id: variant.variant_id,
                        name: variant.name,
                        price: variant.price,
                        weight: variant.weight,
                        key: db.createKey([basics.product_id, basics.name,
                                           variant.variant_id, variant.name])}
              })
  };
  return product;
}

// PG request to select all brands and companies
function brandsRequest(callback) {
  pg.connect(config, function onConnected(err, client, done) {
    if (err) return callback(err);
    var str = "SELECT c.company_id, c.name, c.in_navbar,\
      b.brand_id as brand_id, b.name as brand_name,\
      b.in_navbar as brand_navbar\
      FROM product_info.company c\
      LEFT JOIN product_info.brand b ON b.company_id = c.company_id\
      ORDER BY c.company_id";
    client.query(str, function onBrandQuery(err, result) {
      if (err) {
        done();
        return callback(err);
      }
      var brandTree = createBrandTree(result.rows);
      callback(null, brandTree);
      done();
    });
  });
}

// creates the company/brand tree from brandsRequest result
function createBrandTree(brandsList) {
  var brandTree = [];
  var currentCompany = null;
  for (var i=0; i<brandsList.length; i++) {
    var line = brandsList[i];
    if (currentCompany == null || line.company_id != currentCompany.id) {
      currentCompany = {id:line.company_id,
                        name:line.name,
                        in_navbar:line.in_navbar,
                        brands:[]};
      brandTree.push(currentCompany);
    }
    currentCompany.brands.push({id:line.brand_id,
                                name:line.brand_name,
                                in_navbar:line.brand_navbar});
  }
  return brandTree;
}

// Only keeps brands that are in_navbar
function filterBrands(brandTree) {
  var filteredTree = [];
  var others = {id:-1, name:'Others', in_navbar:true, brands:[]};
  var currentCompany = null;
  filteredTree.push(others);
  for (var ic=0; ic<brandTree.length; ic++) {
    if (brandTree[ic].in_navbar == true) {
      currentCompany = {id:brandTree[ic].id, name:brandTree[ic].name,
                        in_navbar:brandTree[ic].in_navbar, brands:[]};
      filteredTree.push(currentCompany);
    } else {
      currentCompany = others;
    }
    for (var ib=0; ib<brandTree[ic].brands.length; ib++) {
      var brand = brandTree[ic].brands[ib];
      var brandCopy = {id:brand.id, name:brand.name,
                       in_navbar:brand.in_navbar};
      if (brandCopy.in_navbar == true) currentCompany.brands.push(brandCopy);
    }
  }
  return filteredTree;
}

// PG request to select all categories and create tree
function categoriesRequest(callback) {
  pg.connect(config, function onConnected(err, client, done) {
    if (err) return callback(err);
    var str = "SELECT child.category_id as id, child.name,\
               parent.category_id as parent_id\
               FROM product_info.category child\
               LEFT JOIN product_info.category parent\
                ON child.parent_id = parent.category_id\
               ORDER BY 1";
    client.query(str, function onCategoryQuery(err, result) {
      if (err) {
        done();
        return callback(err);
      }
      var categoryTree = createCategoryTree(result.rows);
      callback(null, categoryTree);
      done();
    });
  });
}

// creates category tree from categoriesRequest result
function createCategoryTree(categories) {
  var categoryTree = []; // real tree
  var dict = {}; // easy access of previously accessed cat by ID
  while (categories.length > 0)  {
    var cat = categories.shift();
    if (cat.children == undefined) {
      cat.children = [];
    }
    dict[cat.id] = cat;
    if (dict[cat.parent_id] != undefined) {
      dict[cat.parent_id].children.push(cat);
      delete cat.parent_id;
    } else if (cat.parent_id != null) {
      // didn't meet the parent yet... let's put it at the end again
      categories.push(cat);
    } else {
      // it's a root!
      categoryTree.push(cat);
      delete cat.parent_id;
    }
  }
  return categoryTree;
}

// helper functions


// Replaces all occurences of 'find' by 'replace' in 'str'
function replaceAll(find, replace, str) {
  return str.replace(new RegExp(find, 'g'), replace);
}




module.exports = db;