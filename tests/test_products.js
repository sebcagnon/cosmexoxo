var productsDB = require ('../models/products.js');

console.log('List of Brands:');
console.log(productsDB.getBrandList());
console.log('\n');

console.log('List of Shiseido products:');
console.log(productsDB.getProductsByBrand('Shiseido')) ;
console.log('\n');

console.log('Shiseido is a brand? (true): ' + productsDB.isBrand('Shiseido'));

console.log('NotABrand is a brand? (false): ' + productsDB.isBrand('NotABrand'));