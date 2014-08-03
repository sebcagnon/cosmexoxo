var shippingFees = require('./shippingCost.json')
  , nconf = require('nconf');

nconf.env().file('./.env');
var yenToDollars = nconf.get('YENTODOLLARS');

var utils = {
  // returns the HTML for links
  link_to : function (target, text, addedHTML) {
    var resultStr = '<a href="' + encodeURI(target) + '"';
    if (addedHTML != undefined) resultStr += ' ' + addedHTML;
    resultStr += '>' + text + '</a>';
    return resultStr;
  },

  // returns the HTML for displaying the category tree
  displayCategoryTree : function (categoryTree, n, isMain) {
    if (categoryTree.length == 0) return '';
    var space = Array(n).join('  ');
    if (isMain == 1) {
      var resultStr = '\n' + space + '<ul class="columns2">';
    } else {
      var resultStr = '\n' + space + '<ul>';
    }
    for (var i=0; i<categoryTree.length; i++) {
      resultStr += '\n' + space + '  <li>';
      if (isMain == 0) resultStr += '<h2>'
      resultStr += utils.link_to('/categories/' + categoryTree[i].name,
                                 categoryTree[i].name);
      if (isMain == 0) resultStr += '</h2>'
      resultStr += utils.displayCategoryTree(categoryTree[i].children,
                                             n+2,
                                             isMain+1);
      resultStr += '\n' + space + '  </li>'
    }
    resultStr += '\n' + space + '</ul>';
    return resultStr;
  },

  // creates the html for a responsive image
  responsiveImage : function (link, alt, title) {
    title = title || alt;
    return '<img class="img-responsive" src="' + link + '" alt="' + alt +
            '" title="' + title + '">';
  },

  // computes shipping costs from country and weight
  getShippingCost : function (country, weight) {
    for (var i=0; i<shippingFees.zones.length; i++) {
      var zone = shippingFees.zones[i];
      if (shippingFees[zone].countries.indexOf(country) != -1) {
        var currentRange = 10000;
        var price = 0;
        var maxPrice = 0;
        for (w in shippingFees[zone].price) {
          if (parseInt(w) < currentRange && parseInt(w) >= parseInt(weight)) {
            currentRange = w;
            price = shippingFees[zone].price[w];
          }
          if (parseInt(shippingFees[zone].price[w]) >= parseInt(maxPrice)) {
            maxPrice = shippingFees[zone].price[w];
          }
        }
        // if order is too heavy
        if (price == 0) {
          price = maxPrice;
        }
        return Math.ceil(parseInt(price)*parseFloat(yenToDollars)).toString();
      }
    }
    return; // could not find country, return undefined
  },

  // returns the list of available countries
  getAvailableCountries : function () {
    var retList = [];
    for (var i=0; i<shippingFees.zones.length; i++) {
      var zone = shippingFees.zones[i];
      retList = retList.concat(shippingFees[zone].countries);
    }
    retList.sort();
    return retList;
  }
}; // end of exported functions

module.exports = utils;