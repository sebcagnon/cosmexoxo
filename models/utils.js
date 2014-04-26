

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
  }
}; // end of exported functions

module.exports = utils;