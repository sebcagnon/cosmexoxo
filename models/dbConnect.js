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
  // Allow to retrieve pg config to use in other modules (ex: cookie session)
  getConfig : function () {
    return config;
  },

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

  // Returns a list of all products that are featured for home page
  getFeaturedProducts : function (callback) {
    pg.connect(config, function featuredProductsQuery(err, client, done) {
      if (err) callback(err);
      var str = 'SELECT p.product_id, p.name, p.description as desc,\
                 b.name as brandname\
                 FROM product_info.product p\
                 LEFT JOIN product_info.brand b ON p.brand_id = b.brand_id\
                 WHERE p.featured = true';
      client.query(str, function onQueryFinished(err, result) {
        if (err) {
          callback(err);
        } else {
          callback(null, _.map(result.rows, addKeys));
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
          callback(null, _.map(result.rows, addKeys));
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

  // returns a list of products belonging to category: categoryName
  getProductsByCategory : function (categoryName, callback) {
    pg.connect(config, function prodByCatQuery(err, client, done) {
      if (err) return callback(err);
      var str = 'SELECT p.product_id, p.name, p.description as desc,\
                 b.name as brandname\
                 FROM product_info.product p\
                 INNER JOIN product_info.product_category pc\
                  ON p.product_id = pc.product_id\
                 INNER JOIN product_info.category c\
                  ON pc.category_id = c.category_id\
                 INNER JOIN product_info.brand b\
                  ON p.brand_id = b.brand_id\
                 WHERE c.name = $1';
      client.query(str, [categoryName], function onQueryFinished(err, result) {
        if (err) {
          callback(err);
        } else {
          callback(null, _.map(result.rows, addKeys));
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

  // creates a new row in order and add its variants into order_variant
  createOrder : function (cart, shipping, callback) {
    createNewOrder(cart, shipping, function onOrderCreated (err, orderId) {
      if (err) return callback(err);
      var invoiceNumber = createInvoiceNumber(orderId);
      createOrderVariant(cart, orderId, function onOrderReady (err) {
        if (err) return callback(err);
        callback(null, orderId, invoiceNumber);
      });
    });
  },

  // updates the "order" table for the fields using whereParams in WHERE clause
  updateOrder : function (fields, whereParams, callback) {
    pg.connect(config, function updateOrderQuery (err, client, done) {
      if (err) return callback(err);
      var setItems = [];
      var params = [];
      var i = 1;
      for(var item in fields) {
        setItems.push(item.toString() + '= $' + i);
        i += 1;
        params.push(fields[item]);
      }
      var str = 'UPDATE product_info."order" SET _ITEMS_\
                 WHERE ' + whereParams[0] + ' = $' + i;
      str = replaceAll('_ITEMS_', setItems.join(', '), str);
      params.push(whereParams[1]);
      client.query(str, params, function onOrderUpdated (err) {
        if (err) {
          callback(err)
        } else {
          callback();
        }
        done();
      });
    });
  },

  // creates address and returns its address_id
  createAddress : function (fields, callback) {
    pg.connect(config, function insertAddressQuery (err, client, done) {
      if (err) return callback(err);
      var setItems = [], dollars = [], params = [], i = 1;
      for (var item in fields) {
        setItems.push(item.toString());
        dollars.push('$' + i);
        i += 1;
        params.push(fields[item]);
      }
      var str = 'INSERT INTO product_info.address (_HEADERS_)\
                 VALUES (_VALUES_) RETURNING address_id';
      str = replaceAll('_HEADERS_', setItems.join(', '), str);
      str = replaceAll('_VALUES_', dollars.join(', '), str);
      client.query(str, params, function onAddressInserted (err, result) {
        if (err) {
          callback(err);
        } else if (result.rows.length == 0) {
          callback('no value returned when inserting address');
        } else {
          callback(null, result.rows[0].address_id);
        }
        done();
      });
    });
  },

  // retrieves the total weight of the variants in the order
  getOrderWeight : function (invoiceNumber, callback) {
    pg.connect(config, function getWeightQuery (err, client, done) {
      if (err) return callback(err);
      var str = 'SELECT v.weight, ov.quantity\
                 FROM product_info.order o\
                 INNER JOIN product_info.order_variant ov\
                  ON o.order_id = ov.order_id\
                 INNER JOIN product_info.variant v\
                  ON ov.variant_id = v.variant_id\
                 WHERE o.invoice_number = $1';
      client.query(str, [invoiceNumber], function onVariantsList(err, result) {
        if (err || !result.rows.length) {
          callback(err || 'no variants found');
        } else {
          var getWeight = function (prev, curr, ind, arr) {
            return prev + curr.weight * curr.quantity;
          };
          var orderWeight = result.rows.reduce(getWeight, 0);
          callback(null, orderWeight);
        }
        done();
      });
    });
  },

  // retrieves all the info the customer needs about his order
  getOrderInfo: function (invoiceNumber, callback) {
    pg.connect(config, function orderInfoQuery (err, client, done) {
      if (err) return callback(err);
      var str =
"SELECT o.invoice_number, o.firstname, o.lastname, o.email, o.total_amount, \
  o.item_amount, o.shipping_amount, o.checkoutstatus, o.phone_number, \
  o.shipping_type, a.name as shipname, a.street, a.street2, a.city, a.zip, \
  a.country_code, a.country, a.state, v.name, p.name as productName, \
  ov.quantity, ov.unit_price, b.name as brandName \
FROM product_info.order o \
LEFT JOIN product_info.address a ON a.address_id = o.shipping_address_id \
LEFT JOIN product_info.order_variant ov ON o.order_id = ov.order_id \
LEFT JOIN product_info.variant v ON ov.variant_id = v.variant_id \
LEFT JOIN product_info.product p ON p.product_id = v.product_id \
LEFT JOIN product_info.brand b ON b.brand_id = p.brand_id \
WHERE o.invoice_number = $1;"
      client.query(str, [invoiceNumber], function onOrderInfo (err, result) {
        if (err) {
          done();
          return callback(err);
        }
        var row0 = result.rows[0];
        order = {};

        // /!\ depends of for (... in ...) keeping the order
        var i = 0;
        for (var prop in row0) {
          // copy order basics
          if (i<10) {
            order[prop] = row0[prop];
          } else if (i==10) {
            order.address = {name:row0[prop]};
          } else if (i<18) {
            order.address[prop] = row0[prop];
          }
          i++;
        }
        order.variants = [];
        for (var i=0; i<result.rows.length; i++) {
          var v = result.rows[i];
          order.variants.push(
            {
              name: v.name,
              productName: v.productname,
              brandName: v.brandname,
              quantity: v.quantity,
              price: v.unit_price
            }
          );
        }
        done();
        callback(null, order);
      });
    });
  },

  // retrieves the list of all orders with status Completed
  getOrdersToShip: function (callback) {
    pg.connect(config, function getOrdersQuery (err, client, done) {
      var str =
        "SELECT invoice_number, creation_date, total_amount, checkoutstatus\
          FROM product_info.order\
          WHERE checkoutstatus = 'Completed'\
          ORDER BY creation_date;"
      client.query(str, function onOrdersList (err, result) {
        done();
        callback(err, result.rows);
      });
    });
  },

  // Closes remaining connections to the database
  // after queries have all returned
  // to allow for programs to finish nicely.
  close : function () {
    pg.end();
  },

  // Creates a key for AWS S3 from products/variants name and id
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
                        price: parseInt(variant.price),
                        weight: parseInt(variant.weight),
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
  filteredTree.push(others);
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

// adds S3 key and link URL the product objects
function addKeys (row) {
  row.key = db.createKey([row.product_id, row.name]);
  row.link = '/product/' + row.product_id;
  return row;
}

// creates a new row in order table
function createNewOrder (cart, shipping, callback) {
  pg.connect(config, function onConnected(err, client, done) {
    if (err) return callback(err);
    var params = [cart.shippingamt+cart.itemamt, cart.shippingamt,
                  cart.itemamt, shipping.type]
    if (shipping.type == 'EMS') {
      var str = 'INSERT INTO product_info."order"\
                (total_amount, shipping_amount, item_amount, shipping_type,\
                 phone_number)\
                VALUES ($1, $2, $3, $4, $5)\
                RETURNING order_id';
      params.push(shipping.phone);
    } else {
      var str = 'INSERT INTO product_info."order"\
                (total_amount, shipping_amount, item_amount, shipping_type)\
                VALUES ($1, $2, $3, $4)\
                RETURNING order_id';
    }
    client.query(
      str,
      params,
      function onOrderInserted (err, result) {
        if (err) {
          callback(err);
        } else if (result.rows.length == 0) {
          callback('no order_id was returned when creating the order');
        } else {
          callback(null, result.rows[0].order_id);
        }
        done();
    });
  });
}

function createOrderVariant (cart, order_id, callback) {
  pg.connect(config, function onConnected(err, client, done) {
    if (err) return callback(err);
    var str = 'INSERT INTO product_info.order_variant\
                (order_id, variant_id, quantity, unit_price)\
               VALUES '
    for (var i=0; i<cart.length; i++) {
      var item = cart[i];
      var line = '(';
      if (i>0) line = ', ' + line;
      line += [order_id, item.variant.variant_id,
               item.quantity, item.variant.price].join(", ");
      line += ')';
      str += line;
    }
    client.query(str, function onInsertedOrderVariant (err) {
      callback(err);
      done();
    });
  });
}

// creates an invoice number from an order_id
function createInvoiceNumber(orderId) {
  var d = new Date();
  return 'INV' + d.getFullYear() + 0 + (d.getMonth() + 1) + orderId;
}

// helper functions

// Replaces all occurences of 'find' by 'replace' in 'str'
function replaceAll(find, replace, str) {
  return str.replace(new RegExp(find, 'g'), replace);
}


module.exports = db;