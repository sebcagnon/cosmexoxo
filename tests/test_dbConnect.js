var db = require('../models/dbConnect');

console.log('Testing key function');
var arr = [29, 'mascada boom', 40, 'Very-b@d_ke!#'];
if (!db.createKey(arr)=='29_mascada-boom_40_Very-bd_ke') {
  throw 'Error in createKey: ' + db.createKey(arr) || 'AssertionError';
}
var arr2 = [34, '[/hello>*|}"', 35, 'how are you'];
if (!db.createKey(arr2)=='34_hello_35_how-are-you') {
  throw 'Error in createKey: ' + db.createKey(arr2) || 'AssertionError';
}

console.log('Testing getConfig:');
console.log(db.getConfig());

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
  db.getProductsByBrand('Elixir', testGetProductsByBrand);
}

function testGetProductsByBrand(err, result) {
  if (err) {
    console.log('Error in getProductsByBrand: ' + err);
    db.close();
    return;
  }
  console.log('getProductsByBrand result:');
  console.log(result);
  db.getAllCategories(testGetAllCategories);
}

function testGetAllCategories(err, result) {
  if (err) {
    console.log('Error in getAllCategories: ' + err);
    db.close();
    return;
  }
  console.log('getAllCategories result:');
  console.log('Raw:');
  console.log(result);
  console.log('Pretty:');
  for (var i=0; i<result.length; i++) {
    displayCategoryNode(result[i], 1);
  }
  console.log('findSubTree results:')
  console.log(db.findSubTree('Mascara', result));
  db.getProductsByCategory('Shampoo', testGetProductsByCategory);
}

function testGetProductsByCategory(err, result) {
  if (err) {
    console.log('Error in getProductsByCategory: ' + err);
    db.close();
    return;
  }
  console.log('getProductsByCategory result:');
  console.log(result);
  db.getFeaturedProducts(testGetFeaturedProducts);
}

function testGetFeaturedProducts(err, result) {
  if (err) {
    console.log('Error in getFeaturedProducts: ' + err);
    db.close();
    return;
  }
  console.log('getFeaturedProducts result:');
  console.log(result);
  var cart = [
    {quantity: 2, variant:{variant_id:47, price:15}},
    {quantity: 1, variant:{variant_id:38, price:10}}
  ];
  cart.itemamt = 40;
  cart.shippingamt = 15;
  db.createOrder(cart, testCreateOrder);
}

function testCreateOrder(err, ids) {
  if (err) {
    console.log('Error in createOrder: ' + err);
    db.close();
    return;
  }
  console.log('createOrder returned following ids: ' + ids);
  db.updateOrder({invoice_number:ids[1], token:'EC-ABCD1234'},
                 ['order_id', ids[0]],
                 testUpdateOrder);
}

function testUpdateOrder(err) {
  if (err) {
    console.log('Error in updateOrder: ' + err);
    return db.close();
  }
  console.log('updateOrder succeeded! (no result)');
  db.createAddress(
    {
      name: 'Seb Cag',
      street: '1-1-1 Aoyama',
      street2: 'Paypal Building 101',
      city: 'Bunkyo',
      zip: '113-0031',
      country_code: 'JP',
      country: 'Japan',
      state: 'Tokyo'
    },
    testCreateAddress);
}

function testCreateAddress(err, address_id) {
  if (err) {
    console.log('Error in createAddress: ' + err);
    return db.close();
  }
  console.log('createAddress returned address_id: ' + address_id);
  onFinished();
}

function onFinished() {
  console.log('Finished!');
  db.close();
}

db.getProduct(24, testGetProduct1);


// helper functions

// displays a node and prints all its children with one more tab
function displayCategoryNode(node, n) {
  var space = Array(n).join('\t');
  console.log(space + node.id + ': ' + node.name);
  for (var i=0; i<node.children.length; i++) {
    displayCategoryNode(node.children[i], n+1);
  }
}