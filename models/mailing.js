var nodemailer = require("nodemailer")
  , nconf = require('nconf');

nconf.env().file('./.env');

var smtpTransport = nodemailer.createTransport("SMTP", {
  service: "Gmail",
  auth: {
    user: nconf.get('MAILING_AUTH_USER'),
    pass: nconf.get('MAILING_AUTH_PASS')
  }
});
var from = nconf.get('MAILING_FROM');
var owner = nconf.get('MAILING_OWNER_EMAIL');

var mailing = {
  // sends an email when an order was received
  sendNewOrder: function(orderInfo, callback) {
    html  = 'Hello,<br><br>';
    html += 'Congratulations, you received a new order on CosmeXO!<br>';
    html += 'Invoice number: ' + orderInfo.invoice_number + '<br><br>';
    html += createOrderConfirmationHTML(orderInfo);
    mailOptions = {
      from: from,
      to: owner,
      subject: 'Order ' + orderInfo.invoice_number + ' received on CosmeXO!',
      html: html
    };
    smtpTransport.sendMail(mailOptions, callback);
  },

  // sends an order confirmation email to the customer
  sendOrderConfirmation: function (orderInfo, callback) {
    html = createOrderConfirmationHTML(orderInfo);
    var orderNumber = ''
    if (orderInfo.invoice_number != undefined)
      orderNumber = orderInfo.invoice_number + ' ';
    mailOptions = {
      from: from,
      to: orderInfo.email,
      subject: 'Thank you for your purchase on CosmeXO',
      html: html
    }
    smtpTransport.sendMail(mailOptions, callback);
  },

  // closes the smtpTransport
  close: function() {
    smtpTransport.close();
  }
};


// HELPER FUNCTIONS

// creates the HTML for the order confirmation mail
function createOrderConfirmationHTML(order) {
  html = 'Hello ' + order.firstname + ' ' + order.lastname + '<br><br>';
  html += 'Your invoice number is <b>' + order.invoice_number + '</b>. ';
  html += 'Please include this invoice number in your emails when you contact us. ';
  html += 'For any inquiry, you can contact us at contact@cosmexo.com or just ';
  html += 'reply to this e-mail.<br><br>';
  html += '<h1>Order Summary</h1>';
  html += 'Address:<br>';
  html += order.address.name + '<br>';
  html += order.address.street + ' ' + order.address.street2 + ' ' +
          order.address.city + ' ' + order.address.state + ' ' +
          order.address.zip + ' ' + order.address.country + '.<br>';
  html += 'Purchased items:<br>';
  for (var i=0; i<order.variants.length; i++) {
    var variant = order.variants[i];
    html += variant.name + ' of ' + variant.productName + ': ' +
            variant.quantity + ' * ' + variant.price + '$ = ' +
            (variant.quantity * variant.price) + '$<br>';
  }
  html += 'Shipping cost: ' + order.shipping + '$<br>';
  html += '<b>Total paid: ' + order.totalPrice + '$</b><br><br>';
  html += 'Best regards,<br>The CosmeXO team';
  return html;
}

module.exports = mailing;