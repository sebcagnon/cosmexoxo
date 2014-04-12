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

function callback1(err, result) {
  if (err) {
    console.log('Error in getProduct: ' + err);
    db.close();
    return;
  }
  console.log('getProduct result:');
  console.log(result);
  db.getProductsList(callback2);
}

function callback2(err, result) {
  if (err) {
    console.log('Error in getProductsList: ' + err);
    db.close();
    return;
  }
  console.log('getProductsList result:')
  console.log(result);
  onFinished();
}

function onFinished() {
  console.log('Finished!');
  db.close();
}

db.getProduct(24, callback1);