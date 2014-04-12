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
}

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

  getProductsList : function (callback) {
    pg.connect(config, function onConnected(err, client, done) {
      if (err) return callback(err);
      var str = 'SELECT product_id, name FROM product_info.product';
      client.query(str, function onQueryFinished(err, result) {
        callback(err, result.rows);
        done();
      });
    });
  },

  // Closes remaining connections to the database
  // after queries have all returned
  // to allow for programs to finish nicely.
  close : function () {
    pg.end();
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
    brand_name: basics.brand_name,
    company_name: basics.company_name,
    categories: _.pluck(result[1], 'name'),
    variants: _.map(result[2], function selector(variant) {
                return {variant_id: variant.variant_id,
                        name: variant.name,
                        price: variant.price,
                        weight: variant.weight}
              })
  };
  return product;
}

// helper functions

function replaceAll(find, replace, str) {
  return str.replace(new RegExp(find, 'g'), replace);
}

module.exports = db;