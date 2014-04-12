var displayPrice = require('./public/js/displayPrice')

console.log('0.00:\t' + displayPrice(0));
console.log('1.00:\t' + displayPrice(100));
console.log('12.34:\t' + displayPrice(1234));
console.log('10.30:\t' + displayPrice(1030));
console.log('10,010.00:\t' + displayPrice(1001000));
console.log('102,546.01:\t' + displayPrice(10254601));
console.log('1,000,000,000.00:\t' + displayPrice(100000000000));