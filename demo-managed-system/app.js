var express = require('express');

// Constants
const PORT = 3000;
const HOST = '0.0.0.0';

var app = express();

app.get('/', function (req, res) {
    res.send("alive")
});

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

app.get('/execute_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            o1: {
                type: "integer",
                format: "int64",
                example: 10
            },
            o2: {
                type: "integer",
                format: "int64",
                example: 10                },
        }
    }));
});

app.get('/adaptation_options', function (req, res) {
    res.send(JSON.stringify({
        o1: {
            "values": [10, 12, 14],
            "type": "discrete"
        },
        o2: {
            "values": [5, 15, 20],
            "type": "discrete"
        }
    }));
});

app.get('/adaptation_options_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            o1: {
                "type": "object",
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {
                            "type": "number",
                            "format": "integer",
                            "example": 10
                        }
                    },
                    "type": {
                        "type": "string"
                    }
                }
            },
            o2: {
                "type": "object",
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {
                            "type": "number",
                            "format": "integer",
                            "example": 10
                        }
                    },
                    "type": {
                        "type": "string"
                    }
                }
            }
        }
    }));
});

app.listen(PORT, HOST, () => {
    console.log(`USAS HTTP test app running!! on http://${HOST}:${PORT}`);
});
