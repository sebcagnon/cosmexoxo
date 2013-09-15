var express = require('express')
  , fs = require("fs")
  , engine = require("ejs-locals")
  , http = require('http');

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
});

app.get('/', function(request, response) {
  response.render('index');
});

app.get('/brand/:brandName', function(request, response) {
  formattedName = request.params.brandName[0].toUpperCase() + request.params.brandName.substring(1).toLowerCase();
  response.render('brand', { brandName : formattedName });
});

http.createServer(app).listen(app.get('port'), function () {
  console.log("Listening on " + app.get('port'));
});
