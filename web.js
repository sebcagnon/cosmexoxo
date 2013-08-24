var express = require('express');
var fs = require("fs");

var app = express();
app.use(express.logger());
app.use(express.static(__dirname + '/public'));

app.configure( function () {
  app.set('views', __dirname + '/views');
  app.set('view engine', 'ejs');
  app.use("/public", express.static(__dirname + '/public'));
});

app.get('/', function(request, response) {
  response.render('index');
});

var port = process.env.PORT || 8080;
app.listen(port, function() {
  console.log("Listening on " + port);
});
