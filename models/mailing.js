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
    var html = createOrderConfirmationHTML(orderInfo);
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

  // sends emails in case someone used Contact Us form
  sendContactUs: function (form, callback) {
    var html = createContactUsHTML(form);
    var ownerMail = 'Hello CosmeXO team,<br><br>';
    ownerMail += 'You have received a mail through the websites '
    ownerMail += 'Contact Form<br><br>';
    ownerMail += html;
    var mailOptions = {
      from: from,
      to: owner,
      subject: 'CosmeXO Contact Form: ' + form.name + ' has a question',
      html: ownerMail
    };
    smtpTransport.sendMail(mailOptions, function sendConfirmationMail (err) {
      if (err) return callback(err);
      mailOptions.to = form.email;
      mailOptions.subject = 'Thank you for contacting us, ' + form.name;
      var clientMail = 'Thank you for contacting us, ' + form.name + '<br><br>';
      clientMail += 'We will answer you within a few days.<br><br>';
      clientMail += 'Here is a copy of your message:<br>';
      clientMail += html;
      mailOptions.html = clientMail;
      smtpTransport.sendMail(mailOptions, function finishedSending (err) {
        callback(null); // this mail is not critical, so we don't check err
      });
    });
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
  var address = order.address;
  var addressArray = [address.street, address.street2, address.city,
                      address.state, address.zip, address.country]
  for (var i=0; i<addressArray.length; i++) {
    if (addressArray[i]) html += addressArray[i] + ' ';
  }
  html += '<br>Shipping service: ' + shippingTypeToText(order.shipping_type);
  if (order.phone_number) {
    html += '<br>Phone Number: ' + order.phone_number;
  }
  html += '<br>';
  html += 'Purchased items:<br>';
  for (var i=0; i<order.variants.length; i++) {
    var v = order.variants[i];
    html += v.name + ' of ' + v.productName + ' by ' + v.brandName + ': ';
    html += v.quantity + ' * ' + v.price + '$ = ';
    html += (v.quantity * v.price) + '$<br>';
  }
  html += 'Shipping cost: ' + order.shipping_amount + '$<br>';
  html += '<b>Total paid: ' + order.total_amount + '$</b><br><br>';
  html += 'Best regards,<br>The CosmeXO team';
  return html;
}

function createContactUsHTML(form) {
  var html = 'Name: ' + form.name + '<br>';
  html += 'Email: ' + form.email + '<br>';
  html += 'InvoiceNumber: ' + form.invoiceNumber + '<br>';
  html += 'Message:<br>' + form.message + '<br><br>';
  html += 'Best regards,<br>The CosmeXO team';
  return html;
}

function shippingTypeToText(shippingType) {
  if (shippingType == 'ePacket') {
    return 'Registered International';
  } else {
    return shippingType;
  }
}

module.exports = mailing;