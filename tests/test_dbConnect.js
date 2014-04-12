var db = require('../models/dbConnect')

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