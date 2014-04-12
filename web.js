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
  app.locals.displayPrice = require('./public/js/displayPrice');
});

app.get('/', function(request, response) {
  response.render('index');
});

app.get('/brand/:brandName', function(request, response) {
  var name = request.params.brandName;
  var newName = name[0].toUpperCase() + name.substring(1).toLowerCase();
  if ( products.isBrand(name) ) {
    response.render('brand', { isBrand:true,
                               brandName:newName,
                               products:products.getProductsByBrand(newName)});
  } else {
    response.render('brand', { isBrand:false,
                               brandName:formattedName,
                               brands:products.getBrandList()});
  }
});

app.get('/brand/', function(request, response) {
  response.render('brand', { isBrand:false,
                             brandName:'',
                             brands:products.getBrandList()});
});

app.get('/product/:productID', function(request, response) {
  productData = {};
  response.render('product', productData);
});

// debug function to show all products available
app.get('/products', function(request, response) {
  db.getProductsList(function getProducsCallback(err, productList) {
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
