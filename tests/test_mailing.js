var mailing = require('../models/mailing')
  , nconf = require('nconf');

nconf.env().file('./.env');
var ownerEmail = nconf.get('MAILING_OWNER_EMAIL');

function onFinished() {
  console.log('Finished!');
  mailing.close();
}

function testSendNewOrder(err) {
  if (err) {
    console.log('Error in sendNewOrder: ' + err);
    onFinished();
  } else {
    console.log('sendNewOrder success!');
    mailing.sendOrderConfirmation(order, testSendOrderConfirmation);
  }
}

function testSendOrderConfirmation(err) {
  if (err) {
    console.log('Error in sendOrderConfirmation: ' + err);
    onFinished();
  } else {
    console.log('sendOrderConfirmation success!');
    onFinished();
  }
}

var order = {
  firstname: 'Test',
  lastname: 'User',
  email: ownerEmail,
  invoice_number: 'ABC123456001',
  address: {
    name: 'Test User',
    street: '3 rue de la prairie',
    street2: 'Batiment H1',
    city: 'Paris',
    state: '',
    zip: '75001',
    country: 'France',
    countrycode: 'FRA'
  },
  variants: [
    {
      name: 'Color Red',
      productName: 'Lipstick',
      quantity: 2,
      price: 15
    },
    {
      name: 'RST 17',
      productName: 'Meye Shadow',
      quantity: 1,
      price: 29
    }
  ],
  shipping: 20,
  totalPrice: 79
};

mailing.sendNewOrder(order, testSendNewOrder);