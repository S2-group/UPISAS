var express = require('express');
var bodyParser = require('body-parser')
var app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

app.get('/adaptations', function (req, res) {
    res.send(JSON.stringify({
        schema_all: {
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
        schema_single: {
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
        },
        values: {
            o1: [10, 12, 14],
            o2: [5, 15, 20]
        }
    }));
});

app.listen(3000, function () {
    console.log('USAS HTTP test app listening on port 3000!');
});
