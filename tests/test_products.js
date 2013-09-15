var productsDB = require ('../models/products.js');

console.log(productsDB.getBrandList());

console.log(productsDB.getProductsByBrand('Shiseido'));