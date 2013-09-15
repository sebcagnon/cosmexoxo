module.exports = function (priceInt) {
  var cents = priceInt % 100;
  var rest = (priceInt - cents)/100;
  if (cents < 10) {
    var res = '.0' + cents;
  } else {
    var res = '.' + cents;
  }
  if (rest == 0) {
    return '0' + res;
  }
  var needComma = 0;
  while (rest !== 0) {
    var slice = rest % 1000;
    if (needComma) {
      res = ',' + res;
    } else {
      needComma = 1;
    }
    res = slice + res;
    rest = (rest - slice)/1000;
    if (rest) {
      res = ['', '0', '00'][3-slice.toString().length] + res;
    }
  }
  return res;
}