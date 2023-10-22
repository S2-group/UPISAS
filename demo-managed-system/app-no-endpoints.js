var express = require('express');

// Constants
const PORT = 3000;
const HOST = '0.0.0.0';

var app = express();

app.get('/', function (req, res) {
    res.send("alive")
});

app.listen(PORT, HOST, () => {
    console.log(`USAS HTTP test app running!! on http://${HOST}:${PORT}`);
});
