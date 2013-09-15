var products = require('./products.json');
  //, uu = require('underscore');

var productsDB = new Object();
productsDB.db = products;
productsDB.getBrandList = function () {
  var brands = [];
  for (id in this.db) {
    if ( brands.indexOf(this.db[id]['brand'].toLowerCase()) == -1) {
      brands.push(this.db[id]['brand'].toLowerCase());
    }
  }
  return brands;
}

productsDB.getProductsByBrand = function (brandName) {
  var prods = {};
  for (id in this.db) {
    if ( this.db[id]['brand'].toLowerCase() == brandName.toLowerCase() ) {
      prods[id] = this.db[id];
    }
  }
  return prods;
}

productsDB.isBrand = function (brandName) {
  return productsDB.getBrandList().indexOf(brandName.toLowerCase()) !== -1;
}

module.exports = productsDB;