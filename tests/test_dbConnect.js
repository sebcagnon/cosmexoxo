var db = require('../models/dbConnect')

console.log('Testing key function');
var arr = [29, 'mascada boom', 40, 'Very-b@d_ke!#'];
if (!db.createKey(arr)=='29_mascada-boom_40_Very-bd_ke') {
  throw 'Error in createKey: ' + db.createKey(arr) || 'AssertionError';
}
var arr2 = [34, '[/hello>*|}"', 35, 'how are you'];
if (!db.createKey(arr2)=='34_hello_35_how-are-you') {
  throw 'Error in createKey: ' + db.createKey(arr2) || 'AssertionError';
}

console.log("Testing getProduct");

function testGetProduct1(err, result) {
  if (err) {
    console.log('Error in getProduct: ' + err);
    db.close();
    return;
  }
  console.log('getProduct result:');
  console.log(result);
  db.getProductsList(testGetProductsList);
}

function testGetProductsList(err, result) {
  if (err) {
    console.log('Error in getProductsList: ' + err);
    db.close();
    return;
  }
  console.log('getProductsList result:')
  console.log(result);
  db.getAllBrands(testBrandTree);
}

function testBrandTree(err, result) {
  if (err) {
    console.log('Error in getAllBrands: ' + err);
    db.close();
    return;
  }
  console.log('getAllBrands result:');
  console.log(result);
  var company = result[0];
  console.log(company.name + '\'s brands:')
  for (var i=0; i<company.brands.length; i++) {
    console.log(company.brands[i]);
  }
  db.getNavbarBrands(testGetNavbarBrands);
}

function testGetNavbarBrands(err, result) {
  if (err) {
    console.log('Error in getAllBrands: ' + err);
    db.close();
    return;
  }
  console.log('getNavbarBrands result:');
  console.log(result);
  onFinished();
}

function onFinished() {
  console.log('Finished!');
  db.close();
}

db.getProduct(24, testGetProduct1);