var pg = require('pg');
var fs = require('fs');

// initializing db values

var PGPASS_FILE = '../.pgpass';
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

var schema = "product_info"

module.exports = {

  getProduct : function (productId, onSuccess, onError) {
    pg.connect(config, function(err, client, done) {
      if (err) {
        onError(err);
      } else {
        str = "SELECT p.product_id, p.name, p.description, p.active,\
        b.brand_id, b.name as brand_name, c.company_id,\
        c.name as company_name\
        FROM SCHEMA.product p\
        INNER JOIN SCHEMA.brand b ON p.brand_id = b.brand_id\
        INNER JOIN SCHEMA.company c ON b.company_id = c.company_id\
        WHERE p.product_id = $1"
        newStr = replaceAll('SCHEMA', schema, str);
        client.query(newStr, [productId], function (err, result) {
          if (err) {
            onError(err);
          } else {
            onSuccess(result);
          }
          done();
        });
      }
    });
  },

  getProducts : function () {
    pg.connect(config, function(err, client, done) {
      if(err) return console.error(err);
      client.query('SELECT * FROM product_info.product', function(err, result) {
    	  done();
    	  if(err) return console.error(err);
    	  console.log(result.rows);
      });
  	pg.end()
    });
  }

} // end of exported functions

// helper functions

function replaceAll(find, replace, str) {
  return str.replace(new RegExp(find, 'g'), replace);
}

