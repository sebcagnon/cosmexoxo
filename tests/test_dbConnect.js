var dbConnect = require('../models/dbConnect.js')

console.log("Testing getProduct");
successCb = function(result) {
  console.log("Success!");
  console.log(result);
}
errorCb = function(error) {
  console.log("Error!");
  console.log(error);
}
dbConnect.getProduct(24, successCb, errorCb);
dbConnect.getProduct(16, successCb, errorCb);

console.log('Finished!');
dbConnect.close();