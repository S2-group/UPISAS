var express = require('express');
var bodyParser = require('body-parser')
var app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

app.listen(3000, function () {
    console.log('USAS HTTP test app listening on port 3000!');
});

app.get('/', function (req, res) {
    res.send("alive")
});
