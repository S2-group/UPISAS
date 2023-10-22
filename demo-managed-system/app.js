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

app.get('/possible_adaptations', function (req, res) {
    res.send(JSON.stringify({
        schema: {
            type: "object",
            properties: {
                o1: {
                    type: "array",
                    items: {
                        type: "integer",
                        format: "int64",
                        example: 10
                    }
                },
                o2: {
                    type: "array",
                    items: {
                        type: "integer",
                        format: "int64",
                        example: 10                    }
                },
            }
        },
        values: {
            o1: [10, 12, 14],
            o2: [5, 15, 20]
        }
    }));
});

app.listen(PORT, HOST, () => {
    console.log(`USAS HTTP test app running!! on http://${HOST}:${PORT}`);
});
