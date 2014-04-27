var express = require('express')
  , fs = require("fs")
  , engine = require("ejs-locals")
  , http = require('http')
  , async = require('async')
  , utils = require('./models/utils')
  , db = require('./models/dbConnect'); // product info requests

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

// site wide variables for webpages
app.locals({
  displayPrice: require('./public/js/displayPrice'),
  S3URL: process.env.S3URL || "http://staging-media.cosmexo.com",
  utils: utils
});

// Creates navbar variables and refresh it every day
refreshNavbar(app);
setInterval(refreshNavbar, 24*60*60*1000, app);

// home page
app.get('/', function(request, response) {
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