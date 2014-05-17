var utils = require('../models/utils')
  , db = require('../models/dbConnect');

function testDisplayCategoryTree(err, result) {
  if (err) {
    console.log('Error in getAllCategories: ' + err);
    db.close();
    return;
  }
  var catTree = utils.displayCategoryTree(result, 1);
  console.log('displayCategoryTree result:');
  console.log(catTree);
  onFinished();
}

function onFinished() {
  console.log('Finished!');
  db.close();
}

// start tests by getting all categories
console.log('link_to results:');
console.log(utils.link_to('/categories/Eye Liner', 'Eye Liner products'));
console.log(utils.link_to('/brand/L\'Oréal', 'L\'Oréal', 'class="special"'));
console.log('responsive image:');
console.log(utils.responsiveImage('http://www.example.com/myimage.jpg',
                          "example image"));
console.log('shipping cost calculator:');
console.log('expected: 13; got: ' + utils.getShippingCost('Nepal', '550'));
console.log('expected: 32; got: ' + utils.getShippingCost('Oman', 1400));
console.log('expected: 15; got: ' + utils.getShippingCost('Austria', '100'));
console.log('expected: undefined; got: ' + utils.getShippingCost('b', '100'));
console.log('list of available countries:');
console.log(utils.getAvailableCountries());

db.getAllCategories(testDisplayCategoryTree);