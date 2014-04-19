var express = require('express')
  , fs = require("fs")
  , engine = require("ejs-locals")
  , http = require('http')
  , products = require('./models/products')
  , db = require('./models/dbConnect');

var app = express();
app.use(express.logger());
app.set('port', process.env.PORT || 8080);

app.configure( function () {
  app.set('views', __dirname + '/views');
  app.engine('ejs', engine);
  app.set('view engine', 'ejs');
  app.use("/images", express.static(__dirname + '/public/images'));
  app.use("/styles", express.static(__dirname + '/public/styles'));
  app.use("/bootstrap", express.static(__dirname + '/public/bootstrap'));
  app.use("/js", express.static(__dirname + '/public/js'));
});

app.locals({
  displayPrice: require('./public/js/displayPrice'),
  S3URL: process.env.S3URL || "http://staging-media.cosmexo.com"
});

app.get('/', function(request, response) {
  response.render('index');
});

app.get('/brands/:brandName', function(request, response) {
  var brandName = request.params.brandName;
  db.getProductsByBrand(brandName, function getProdByBrandCb(err, products) {
    if (err || products.length == 0) {
      response.redirect('/brands?nobrand=' + brandName);
    } else {
      response.render('brand', {brandName:brandName, products:products})
    }
  });
});

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

app.get('/product/:productID', function(request, response) {
  db.getProduct(request.params.productID, function getProductCb(err, product) {
    if (err) return response.render('404',
                      {text:'Could not get product: ' + err});
    response.render('product', {product:product});
  });
});

// debug function to show all products available
app.get('/products', function(request, response) {
  db.getProductsList(function getProducsCb(err, productList) {
    if (err) return response.render('404',
                      {text:'Could not get Products list: ' + err});
    response.render('products', {products:productList});
  });
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
