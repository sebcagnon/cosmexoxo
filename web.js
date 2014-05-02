var express = require('express')
  , pgSession = require('connect-pg-simple')(express)
  , engine = require('ejs-locals')
  , http = require('http')
  , paypalxo = require('./models/paypalxo')
  , async = require('async')
  , nconf = require('nconf')
  , exValidator = require('express-validator')
  , utils = require('./models/utils')
  , db = require('./models/dbConnect'); // product info requests

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

// Creates navbar variables and refresh it every day
refreshNavbar(app);
setInterval(refreshNavbar, 24*60*60*1000, app);

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
  console.log(response.locals);
  response.render('index');
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

// adds payment testing page
app.get('/payment', function(request, response) {
  response.render('payment-test', {state:'ask'});
});

app.get('/paymentSuccess', function(request, response) {
  var token = request.query.token;
  var payerid = request.query.PayerID;
  var params = {token:token};
  paypalxo.ec.getExpressCheckoutDetails(params, function (err, details) {
    console.log('CheckoutDetails: \n' + JSON.stringify(details));
  });
  var cart = request.session.cart;
  params.payerid = payerid;
  params.paymentrequest_0_amt= cart.reduce(sumPrice, 0).toString();
  params.paymentrequest_0_currencycode= 'USD';
  params.paymentrequest_0_paymentaction= 'Sale';
  request.session.cart = []; // re-init cart in session
  response.locals.cartSize = 0;
  paypalxo.ec.doExpressCheckoutPayment(params, function (err, answer) {
    console.log('ExpressCheckoutPayment:\n' + JSON.stringify(answer));
    if (err || answer.PAYMENTINFO_0_PAYMENTSTATUS != 'Completed') {
      var params = {
        state:'failed',
        reason: JSON.stringify(err) || answer.PAYMENTINFO_0_PAYMENTSTATUS
      };
      response.render('payment-test', params);
    } else {
      request.session.cart = []; // re-init cart in session
      response.locals.cartSize = 0;
      response.render('payment-test', {state:'success'});
    }
  });
});

app.get('/paymentFailure', function(request, response) {
  response.render('payment-test', {state:'failed', reason:'could not set EC'});
});

// handle paypal button
app.post('/pay', function(request, response) {
  var cart = request.session.cart;
  // Prepare the data
  var data = {
    paymentrequest_0_amt: cart.reduce(sumPrice, 0).toString(),
    paymentrequest_0_itmamt: cart.reduce(sumPrice, 0).toString(),
    paymentrequest_0_currencycode: 'USD',
    returnurl: app.locals.URL + '/paymentSuccess',
    cancelurl: app.locals.URL + '/paymentFailure',
    paymentrequest_0_paymentaction: 'Sale',
    solutiontype: 'Sole',
    landingpage: 'Billing',
    buyeremailoptinenable: 1
  };
  var prefix = 'L_PAYMENTREQUEST_0_';
  for (var i=0; i<cart.length; i++) {
    var item = cart[i];
    data[prefix+'NAME'+i] = item.variant.name + ' of ' + item.name;
    data[prefix+'AMT'+i] = item.variant.price;
    data[prefix+'QTY'+i] = item.quantity;
    data[prefix+'URL'+i] = item.link;
  }
  console.log('setExpressCheckout')
  paypalxo.ec.setExpressCheckout(data, function setECCallback (err, ans) {
    if (err) {
      console.log(err);
      return response.redirect('/paymentFailure');
    }
    // TODO: USE SESSION!!
    app.locals.token = ans.TOKEN;
    return response.redirect(paypalxo.ec.getLoginURL(ans.TOKEN, true));
  });
});

// handles products added to cart
app.post('/addToCart', function (request, response) {
  //validation
  request.checkBody('product_id').notEmpty().isInt();
  request.checkBody('variant_id').notEmpty().isInt();
  request.checkBody('quantity').notEmpty().isInt();
  request.sanitize('product_id').toInt();
  request.sanitize('variant_id').toInt();
  request.sanitize('quantity').toInt();
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
    var data = { cartSize: request.session.cart.length + 1 };
    request.session.cart.push(dbProduct);
    response.send(JSON.stringify(data));
  });
});

app.get('/cart', function (request, response) {
  var cart = request.session.cart;
  cart.itemTotal = cart.reduce(sumPrice, 0);
  response.render('cart', {cart:cart});
});

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

http.createServer(app).listen(app.get('port'), function () {
  console.log("Listening on " + app.get('port'));
});

//called every once in a while to refresh the navbar variables
function refreshNavbar (app) {
  async.parallel([
    db.getNavbarBrands,
    db.getAllCategories
    ],
    function refreshNavbarCb (err, result) {
      if (err) return console.log('Error while updating navbar');
      app.locals.brands = result[0];
      app.locals.categories = result[1];
      console.log('Navbar refreshed');
    });
}

//function to get the sum of the price of all items in the cart
function sumPrice (prev, curr, ind, arr) {
  return prev + curr.variant.price * curr.quantity;
}