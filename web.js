var express = require('express')
  , fs = require("fs")
  , engine = require("ejs-locals")
  , http = require('http')
  , products = require('./models/products');


var app = express();
app.use(express.logger());
app.set('port', process.env.PORT || 8080);

app.configure( function () {
  console.log('setting view engine');
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
  formattedName = request.params.brandName[0].toUpperCase() + request.params.brandName.substring(1).toLowerCase();
  if ( products.isBrand(request.params.brandName) ) {  
    response.render('brand', { isBrand:true, brandName:formattedName, products:products.getProductsByBrand(formattedName)});
  } else {
    response.render('brand', { isBrand:false, brandName:formattedName, brands:products.getBrandList()});
  }
});

app.get('/product/:productID', function(request, response) {
  productData = {};
  response.render('product', productData);
});

http.createServer(app).listen(app.get('port'), function () {
  console.log("Listening on " + app.get('port'));
});
