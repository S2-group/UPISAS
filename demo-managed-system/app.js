var express = require('express');

// Constants
const PORT = 3000;
const HOST = '0.0.0.0';

/**
 * Optimizing function:
 *
 *  Test Range: x:[-4.0-6.0] y:[-10,10]
 *
 *  f(x,y) = 0.4+-1*(0.3*(1-x)*x+y*(2-y)*0.3+x*y/100)
 *
 *  Global minimum at (0.51681, 1.00861) with 0.0198944
 *
 *  Additional random variance can be enabled
 */

var app = express();

var x = 0.0
var y = 0.0

var enableRandom = true

app.get('/', function (req, res) {
    res.send("alive")
});

app.get('/monitor', function (req, res) {
    var rnd = 1
    if (enableRandom) {
        rnd = Math.random()
    }
    res.send(JSON.stringify({
        f: rnd * ( 0.4 + -1 * (0.3 * (1 - x) * x + y * (2 - y) * 0.3 + x * y / 100))
    }));
});

app.put('/execute', function (req, res) {
    if (req.body) {
        console.log("Got value changes: x:" + req.body.x + " - y:" + req.body.y)
        x = req.body.x || x
        y = req.body.y || y
    }
    res.send("ok")
});

app.get('/monitor_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            f: {
                type: "number"
            }
        }
    }));
});

app.get('/execute_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            x: {
                type: "number"
            },
            y: {
                type: "number"
            },
        }
    }));
});

app.get('/adaptation_options', function (req, res) {
    res.send(JSON.stringify({
        x: {
            "start": -4.0,
            "stop": 6.0,
            "type": "continuous"
        },
        y: {
            "start": -10.0,
            "stop": 10.0,
            "type": "continuous"
        }
    }));
});

app.get('/adaptation_options_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            x: {
                type: "object",
                properties: {
                    start: {
                        type: "number"
                    },
                    stop: {
                        type: "number"
                    },
                    type: {
                        type: "string"
                    }
                }
            },
            y: {
                type: "object",
                properties: {
                    start: {
                        type: "number"
                    },
                    stop: {
                        type: "number"
                    },
                    type: {
                        type: "string"
                    }
                }
            }
        }
    }));
});

app.listen(PORT, HOST, () => {
    console.log(`upisas-demo-managed-system running on http://${HOST}:${PORT}`);
});
