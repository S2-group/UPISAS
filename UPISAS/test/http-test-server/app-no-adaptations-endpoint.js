var express = require('express');
var bodyParser = require('body-parser')
var app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

app.get('/monitor', function (req, res) {
    res.send(JSON.stringify({
        i1: 1,
        i2: "42"
    }));
});

app.post('/execute', function (req, res) {
    if (req.body) {
        console.log("Got value changes: o1:" + req.body.o1 + " - o2:" + req.body.o2)
        o1 = req.body.o1 || o1
        o2 = req.body.o2 || o2
    }
    res.send("ok")
});

app.get('/monitor_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            i1: {
                type: "integer",
                format: "int64",
                example: 10
            },
            i2: {
                type: "string",
                example: "10"
            },
        }
    }));
});

app.listen(3000, function () {
    console.log('USAS HTTP test app listening on port 3000!');
});
