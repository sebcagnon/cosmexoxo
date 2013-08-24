var express = require('express');
var fs = require("fs");
var app = express();
app.use(express.logger());
app.use(express.static(__dirname + '/public'));

app.get('/', function(request, response) {
  fs.readfile(__dirname + '/public/index.html', 'utf8', function(err, text) {
    response.send(text);
  });
});

var port = process.env.PORT || 8080;
app.listen(port, function() {
  console.log("Listening on " + port);
});
