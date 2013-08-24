var express = require('express')
  , fs = require("fs")
  , http = require('http');

var app = express();
app.use(express.logger());
app.set('port', process.env.PORT || 8080);

app.configure( function () {
  console.log('setting view engine');
  app.set('views', __dirname + '/views');
  app.set('view engine', 'ejs');
  app.use("/public", express.static(__dirname + '/public'));
});

app.get('/', function(request, response) {
  response.render('index', {});
});

http.createServer(app).listen(app.get('port'), function () {
  console.log("Listening on " + app.get('port'));
});
