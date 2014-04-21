

var utils = {
  // returns the HTML for links
  link_to : function (target, text) {
    return '<a href="' + encodeURI(target) + '">' + text + '</a>';
  },

  // returns the HTML for displaying the category tree
  displayCategoryTree : function (categoryTree, n) {
    if (categoryTree.length == 0) return '';
    var space = Array(n).join('  ');
    var resultStr = '\n' + space + '<ul>';
    for (var i=0; i<categoryTree.length; i++) {
      resultStr += '\n' + space + '  <li>';
      resultStr += utils.link_to('/categories/' + categoryTree[i].name,
                                 categoryTree[i].name);
      resultStr += utils.displayCategoryTree(categoryTree[i].children, n+2);
      resultStr += '\n' + space + '  </li>'
    }
    resultStr += '\n' + space + '</ul>';
    return resultStr;
  }
}; // end of exported functions

module.exports = utils;