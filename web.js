var express = require('express')
  , pgSession = require('connect-pg-simple')(express)
  , engine = require('ejs-locals')
  , http = require('http')
  , paypalxo = require('./models/paypalxo')
  , async = require('async')
  , nconf = require('nconf')
  , exValidator = require('express-validator')
  , utils = require('./models/utils')
  , db = require('./models/dbConnect') // product info requests
  , mailing = require('./models/mailing'); // sending emails

nconf.env().file('./.env');

var app = express();
app.use(express.logger());
app.set('port', nconf.get('PORT') || 8080);

// configures views engine and static content
app.configure( function () {
  app.set('views', __dirname + '/views');
  app.engine('ejs', engine);
  app.set('view engine', 'ejs');
  app.use(express.bodyParser());
  app.use(exValidator());
  app.use("/images", express.static(__dirname + '/public/images'));
  app.use("/styles", express.static(__dirname + '/public/styles'));
  app.use("/js", express.static(__dirname + '/public/js'));
  app.use("/font", express.static(__dirname + '/public/font'));
  app.use("/bootstrap", express.static(__dirname + '/public/bootstrap'));
});

// site wide variables for webpages
app.locals({
  displayPrice: require('./public/js/displayPrice'),
  S3URL: nconf.get('S3URL'),
  utils: utils,
  URL: nconf.get('URL')
});

// sets up cookie session
app.use(express.cookieParser());
app.use(express.session({
  store: new pgSession({
    conString: db.getConfig()
  }),
  secret: nconf.get('COOKIE_SECRET'),
  cookie: {maxAge: 1000*60*60*24*3} // 3 days session
}));

// initialize sessions here
app.use( function (request, response, next) {
  var cart = request.session.cart; // save on synchronous db calls!!
  if (cart == undefined) {
    request.session.cart = [];
    response.locals.cartSize = 0;
  } else {
    response.locals.cartSize = cart.length;
  }
  next();
});

// configure paypalxo API
var paypalString =  nconf.get('PAYPAL');
if (paypalString) {
  paypalxo.configureFromString(paypalString);
} else {
  console.log('could not configure paypalString');
  console.log('Locals: ' + app.locals);
  console.log('paypal: ' + nconf.get('PAYPAL'));
}

// home page
app.get('/', function(request, response) {
  db.getFeaturedProducts(function renderIndex (err, result) {
    if (err) return response.render('index', {products: []});
    response.render('index', {products: result});
  })
});

// displays the products of the brand 'brandName'
app.get('/brands/:brandName', function(request, response) {
  var brandName = decodeURIComponent(request.params.brandName);
  db.getProductsByBrand(brandName, function getProdByBrandCb(err, products) {
    if (err) {
      response.redirect('/brands?nobrand=' + brandName);
    } else {
      response.render('brand', {brandName:brandName, products:products})
    }
  });
});

// displays the list of brands sorted by companies
app.get('/brands', function(request, response) {
  var params = { alert:request.query.nobrand };
  db.getAllBrands(function getAllBrandsCb(err, brandTree) {
    if (err) {
      params.error = err;
      return response.render('brands', params);
    }
    params.error = undefined;
    params.companies = brandTree;
    response.render('brands', params);
  });
});

// displays the products of one category, and the sub-categories
app.get('/categories/:catName', function(request, response) {
  var catName = decodeURIComponent(request.params.catName);
  async.parallel([
    db.getAllCategories,
    async.apply(db.getProductsByCategory, catName)
    ],
    function onCategory(err, result) {
      if (err) {
        response.redirect('/categories?nocategory=' + catName);
      } else {
        var subTree = db.findSubTree(catName, result[0]);
        response.render('category', {catTree:subTree, products:result[1]});
      }
    });
});

// display the hirarchy of categories
app.get('/categories', function(request, response) {
  var params = {alert:request.query.nocategory};
  db.getAllCategories(function getCategoriesCb(err, categories) {
    if (err) {
      params.error = err;
      return response.render('categories', params);
    } else {
      params.error = undefined;
      params.catTree = categories;
      response.render('categories', params);
    }
  });
});

// delivers the individual product pages
app.get('/product/:productID', function(request, response) {
  db.getProduct(request.params.productID, function getProductCb(err, product) {
    if (err) return response.render('404',
                      {text:'Could not get product: ' + err});
    response.render('product', {product:product});
  });
});

// debug page to show all products available
app.get('/products', function(request, response) {
  db.getProductsList(function getProducsCb(err, productList) {
    if (err) return response.render('404',
                      {text:'Could not get Products list: ' + err});
    response.render('products', {products:productList});
  });
});

app.get('/orderVerification', function(request, response) {
  var token = request.query.token;
  var payerid = request.query.PayerID;
  var params = {token:token};
  paypalxo.ec.getExpressCheckoutDetails(params, function (err, details) {
    //console.log('CheckoutDetails: ' + JSON.stringify(details));
    // handle missing ITEMAMT!!
    if (err) {
      console.log(err);
      return response.redirect('/paymentFailure');
    }
    if (details.PAYMENTREQUEST_0_ITEMAMT == undefined) {
      details.PAYMENTREQUEST_0_ITEMAMT =
          (parseInt(details.PAYMENTREQUEST_0_AMT) -
           parseInt(details.PAYMENTREQUEST_0_SHIPPINGAMT)).toString();
    }
    var itemamt = parseInt(details.PAYMENTREQUEST_0_ITEMAMT);
    var country = details.PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME;
    var invoiceNumber = details.PAYMENTREQUEST_0_INVNUM
    db.getOrderWeight(invoiceNumber, function onWeight(err, weight) {
      if (err) {
        console.log(err);
        return response.redirect('/paymentFailure');
      }
      address = {
        name: details.PAYMENTREQUEST_0_SHIPTONAME,
        street: details.PAYMENTREQUEST_0_SHIPTOSTREET,
        street2: details.PAYMENTREQUEST_0_SHIPTOSTREET2,
        city: details.PAYMENTREQUEST_0_SHIPTOCITY,
        zip: details.PAYMENTREQUEST_0_SHIPTOZIP,
        country_code: details.PAYMENTREQUEST_0_SHIPTOCOUNTRYCODE,
        country: details.PAYMENTREQUEST_0_SHIPTOCOUNTRYNAME,
        state: details.PAYMENTREQUEST_0_SHIPTOSTATE
      };
      db.createAddress(address, function onAddressCreated (err, addressID) {
        if (err) {
          console.log(err);
          return response.redirect('/paymentFailure');
        }
        // update Order in DB
        var shippingamt = parseInt(utils.getShippingCost(country, weight));
        params.paymentrequest_0_shippingamt = shippingamt.toString();
        details.PAYMENTREQUEST_0_SHIPPINGAMT = shippingamt.toString();
        params.paymentrequest_0_itemamt = itemamt.toString();
        params.payerid = payerid;
        params.paymentrequest_0_amt = (itemamt + shippingamt).toString();
        if (!details.PAYMENTREQUEST_0_SHIPTOSTREET2)
          details.PAYMENTREQUEST_0_SHIPTOSTREET2 = null;
        fields = {
          email: details.EMAIL,
          payerid: details.PAYERID,
          firstname: details.FIRSTNAME,
          lastname: details.LASTNAME,
          currencycode: details.CURRENCYCODE,
          total_amount: itemamt + shippingamt,
          shipping_amount: shippingamt,
          shipping_address_id: addressID,
          checkoutstatus: 'WaitingForConfirmation'
        };
        where = ['invoice_number', invoiceNumber];
        db.updateOrder(fields, where, function onOrderUpdated (err) {
          if (err) {
            console.log(err);
            return response.redirect('/paymentFailure');
          }
          // prepare answer
          details.PAYMENTREQUEST_0_AMT = params.paymentrequest_0_amt;
          params.paymentrequest_0_currencycode= 'USD';
          params.paymentrequest_0_paymentaction= 'Sale';
          var responseParams = {order: details};
          response.render('orderConfirmation', responseParams);
          request.session.orderParams = params;
          request.session.invoiceNumber = invoiceNumber;
        });
      });
    });
  });
});

app.post('/thankYou', function(request, response) {
  var params = request.session.orderParams;
  paypalxo.ec.doExpressCheckoutPayment(params, function (err, answer) {
    //console.log('ExpressCheckoutPayment:\n' + JSON.stringify(answer));
    if (err || answer.PAYMENTINFO_0_PAYMENTSTATUS != 'Completed') {
      var params = {
        state:'failed',
        reason: JSON.stringify(err) || answer.PAYMENTINFO_0_PAYMENTSTATUS
      };
      response.render('paymentError', params);
    } else {
      var invoiceNumber = request.session.invoiceNumber;
      response.locals.cartSize = 0;
      request.session.cart = []; // re-init cart in session
      db.getOrderInfo(invoiceNumber, function sendMails(err, orderInfo) {
        var resParams = {
          invoiceNumber: invoiceNumber,
          email: orderInfo.email
        };
        response.render('/thankYouPage', resParams);
        mailing.sendOrderConfirmation(orderInfo, function check(err) {
          if (err)
            console.log('error while sending confirmation email: ' + err);
        });
        mailing.sendNewOrder(orderInfo, function check2(err) {
          if (err)
            console.log('error while sending notification email: ' + err);
        });
      });
    }
  });
});

// displayed in case a problem was encountered during payment
app.get('/paymentFailure', function(request, response) {
  var params = {
    state:'failed',
    reason: 'could not process payment'
  };
  response.render('paymentError', params);
});

// handle paypal button
app.post('/pay', function(request, response) {
  var cart = request.session.cart;
  itemamt = cart.reduce(sumPrice, 0);
  weight = cart.reduce(sumWeight, 0);
  shippingamt = parseInt(utils.getShippingCost('United States', weight));
  cart.itemamt = itemamt;
  cart.shippingamt = shippingamt;
  // creating new Order in DB
  db.createOrder(cart, function onOrderCreated(err, orderId, invoiceNumber) {
    // Prepare the data
    if (err) {
      console.log(err);
      response.redirect('/paymentFailure');
    }
    var data = {
      paymentrequest_0_itemamt: itemamt.toString(),
      paymentrequest_0_shippingamt: shippingamt.toString(),
      paymentrequest_0_amt: (itemamt + shippingamt).toString(),
      paymentrequest_0_currencycode: 'USD',
      paymentrequest_0_invnum: invoiceNumber,
      returnurl: app.locals.URL + '/orderVerification',
      cancelurl: app.locals.URL + '/paymentFailure',
      paymentrequest_0_paymentaction: 'Sale',
      solutiontype: 'Sole',
      landingpage: 'Billing',
      buyeremailoptinenable: 1,
      brandname: 'CosmeXO.com' // , invnum: invNum
    };
    var prefix = 'L_PAYMENTREQUEST_0_';
    for (var i=0; i<cart.length; i++) {
      var item = cart[i];
      data[prefix+'NAME'+i] = item.variant.name + ' of ' + item.name;
      data[prefix+'AMT'+i] = item.variant.price;
      data[prefix+'QTY'+i] = item.quantity;
      data[prefix+'URL'+i] = item.link;
    }
    //console.log('setExpressCheckout')
    //console.log(data);
    paypalxo.ec.setExpressCheckout(data, function setECCallback (err, ans) {
      if (err) {
        console.log(err);
        return response.redirect('/paymentFailure');
      }
      // updating Order with invnum and token
      var updateFields = {
        invoice_number: invoiceNumber,
        token: ans.TOKEN,
        checkoutstatus: 'Set'
      };
      var where = ['order_id', orderId];
      db.updateOrder(updateFields, where, function onOrderUpdated (err) {
        if (err) {
          console.log(err);
          return response.redirect('/paymentFailure');
        }
        return response.redirect(paypalxo.ec.getLoginURL(ans.TOKEN));
      });
    });
  });
});

// handles products added to cart
app.post('/addToCart', function (request, response) {
  //validation
  validateRequest(request, withQuantity=true);
  // check for errors
  var errors = request.validationErrors();
  if (errors) {
    console.log("Validation errors in addToCart: " + JSON.stringify(errors));
    return response.send(JSON.stringify({error:'Could not validate input'}));
  }
  var newProduct = {
    product_id: request.param('product_id'),
    variant_id: request.param('variant_id'),
    quantity: request.param('quantity')
  };
  // check if already there
  var cart = request.session.cart;
  for (var i=0; i<cart.length; i++) {
    if (cart[i].variant.variant_id == newProduct.variant_id) {
      cart[i].quantity = newProduct.quantity;
      break;
    }
  }
  if (i<cart.length) {
    var data = {
      cartSize: cart.length,
      cart: cart,
      btnMessage: 'Updated'
    };
    if (request.param('jsenabled')) {
      response.send(JSON.stringify(data));
    } else {
      response.redirect(request.get('Referrer'));
    }
    return request.session.cart = cart;
  }
  // get full data from db
  var dbProduct = db.getProduct(newProduct.product_id,
                                function addProductToCart (err, dbProduct) {
    // replace variants with only 1 variant from order
    for (var i=0; i<dbProduct.variants.length; i++) {
      if (dbProduct.variants[i].variant_id == newProduct.variant_id) {
        dbProduct.variant = dbProduct.variants[i];
      }
    }
    dbProduct.variants = undefined;
    dbProduct.quantity = newProduct.quantity;
    cart.push(dbProduct);
    var data = {
      cartSize: cart.length,
      cart: cart,
      btnMessage: 'Added'
    };
    if (request.param('jsenabled')) {
      response.send(JSON.stringify(data));
    } else {
      response.redirect(request.get('Referrer'));
    }
    request.session.cart = cart;
  });
});

app.post("/removeFromCart", function (request, response) {
  validateRequest(request);
  var errors = request.validationErrors();
  if (errors) {
    console.log("Validation errors in addToCart: " + JSON.stringify(errors));
    return response.send(JSON.stringify({error:'Could not validate input'}));
  }
  var vid = request.param('variant_id');
  var cart = request.session.cart;
  for (var i=0; i<cart.length; i++) {
    if (cart[i].variant.variant_id == vid) {
      cart.splice(i, 1);
      break;
    }
  }
  data = {
    cartSize: cart.length,
    cart: cart,
    removeId: vid,
    btnMessage: 'Removed'
  };
  if (request.param('jsenabled')) {
    response.send(JSON.stringify(data));
  } else {
    response.redirect(request.get('Referrer'));
  }
  request.session.cart = cart;
});

app.post('/changeQuantity', function (request, response) {
  validateRequest(request, withQuantity=true);
  var errors = request.validationErrors();
  if (errors) {
    console.log("Validation errors in changeQuantity: " +
                JSON.stringify(errors));
    return response.send(JSON.stringify({error:'Could not validate input'}));
  }
  var vid = request.param('variant_id');
  var cart = request.session.cart;
  var change = request.param('quantity');
  var data = {}
  for (var i=0; i<cart.length; i++) {
    if (cart[i].variant.variant_id == vid) {
      cart[i].quantity += change;
      if (cart[i].quantity == 0) {
        cart.splice(i, 1);
        data.removeId = vid;
      }
      break;
    }
  }
  data.cartSize = cart.length;
  data.cart = cart;
  if (request.param('jsenabled')) {
    response.send(JSON.stringify(data));
  } else {
    response.redirect(request.get('Referrer'));
  }
  request.session.cart = cart;
});

app.get('/cart', function (request, response) {
  var cart = request.session.cart;
  cart.itemTotal = cart.reduce(sumPrice, 0);
  cart.weightTotal = cart.reduce(sumWeight, 0);
  response.render('cart', {cart:cart});
});

app.get('/contactUs', function (request, response) {
  var params = {};
  if (request.query.status == 'success') {
    params.alert = 'success';
  } else if (request.query.status == 'failure'){
    params.alert = 'failure';
    params.errors = [{param:'', msg:'error unknown'}];
  } else {
    params.alert = 'noalert'
  }
  response.render('contactUs', params);
});

app.post('/contactUs', function (request, response) {
  validateContactUs(request);
  var errors = request.validationErrors();
  params = {};
  if (errors) {
    params.alert = 'failure';
    params.errors = errors;
    response.render('contactUs', params);
  } else {
    form = {
      name: request.param('InputName'),
      email: request.param('InputEmail'),
      invoiceNumber: request.param('InvoiceNumber'),
      message: request.param('InputMessage')
    }
    mailing.sendContactUs(form, function onContactUsMailsSent (err) {
      if (err) {
        params.alert = 'failure';
        params.errors = [{
          param:'',
          msg:'Could not send email to CosmeXO team'
        }];
      } else {
        params.alert = 'success';
      }
      response.render('contactUs', params);
    });
    params.alert = 'success';
    response.render('contactUs', params);
  }
});

app.get('/search', function (request, response) {
  var params = {
    cse_cx:nconf.get('GOOGLE_CSE_CX')
  };
  response.render('searchResults', params);
})

// Handling pages not handled by app.get
app.use(function(req, res, next){
  res.status(404);
  if (req.accepts('html')) {
    res.render('404', { text: req.url });
    return;
  }
  if (req.accepts('json')) {
    res.send({ error: 'Not found' });
    return;
  }
  res.type('txt').send('Not found');
});

// creates the navbar, sets-up navbar refresh rate and starts server

refreshNavbar(app, function onNavbarReady () {
  http.createServer(app).listen(app.get('port'), function onServerStarted() {
    console.log("Listening on " + app.get('port'));
  });
});
setInterval(refreshNavbar, 24*60*60*1000, app);


//called every once in a while to refresh the navbar variables
function refreshNavbar (app, callback) {
  async.parallel([
    db.getNavbarBrands,
    db.getAllCategories
    ],
    function refreshNavbarCb (err, result) {
      if (err) return console.log('Error while updating navbar');
      app.locals.brands = result[0];
      app.locals.categories = result[1];
      console.log('Navbar refreshed');
      if (callback) callback();
    });
}

//function to get the sum of the price of all items in the cart
function sumPrice (prev, curr, ind, arr) {
  return prev + curr.variant.price * curr.quantity;
}

//function to get the sum of the weight of all items in the cart
function sumWeight (prev, curr, ind, arr) {
  return prev + curr.variant.weight * curr.quantity;
}

function validateRequest(request, withQuantity) {
  request.checkBody('product_id').notEmpty().isInt();
  request.checkBody('variant_id').notEmpty().isInt();
  if (withQuantity) request.checkBody('quantity').notEmpty().isInt();
  request.sanitize('product_id').toInt();
  request.sanitize('variant_id').toInt();
  if (withQuantity) request.sanitize('quantity').toInt();
  request.sanitize('jsenabled').toBoolean();
}

function validateContactUs(request) {
  request.checkBody('InputName').notEmpty().isAlphanumeric();
  request.checkBody('InputEmail').notEmpty().isEmail();
  request.checkBody('InvoiceNumber').isAlphanumeric();
  request.checkBody('InputMessage').notEmpty();
}