var dbConnect = require('../models/dbConnect.js')

console.log("Testing getProduct");

function callback1(err, result) {
  if (err) {
    console.log('Error in getProduct: ' + err);
    dbConnect.close();
    return;
  }
  console.log('getProduct result:');
  console.log(result);
  dbConnect.getProductsList(callback2);
}

function callback2(err, result) {
  if (err) {
    console.log('Error in getProductsList: ' + err);
    dbConnect.close();
    return;
  }
  console.log('getProductsList result:')
  console.log(result);
  onFinished();
}

function onFinished() {
  console.log('Finished!');
  dbConnect.close();
}

dbConnect.getProduct(24, callback1);