var express = require('express');

// Constants
const PORT = 3000;
const HOST = '0.0.0.0';

/**
 * Congratulations! Your research proposal has just been accepted and funded by the National Science Foundation.
 * Now you are finally able to send an underwater drone to the Mariana Trench to search for an ancient fish
 * that has been believed extinct. You, however, know that the fish is still alive and you are determined to 
 * find video evidence of it You have an extensive background in self-adaptive systems and you decide to use 
 * your knowledge to develop a system that will help you find the fish. You must be careful though, as the fish 
 * is very elusive and the drone does not have a lot of battery life. You must find the fish and return the 
 * drone to the surface before the battery dies. 
 * 
 * This system makes use of the following data points:
 * - depth: The depth of the drone in meters. The drone can go as deep as 100 meters and as shallow as 0 meters.
 * Every 5 meters the drone goes down or up, the battery life will decrease by 1%. The depth can only change by
 * 1 meter every time interval.
 * 
 * - battery: The battery life of the drone as a percentage. The drone starts with 100% battery life and must
 * return to the surface before the battery reaches 0%. When returning home, the drone cannot go slower than
 * 1 meter per second.
 * 
 * - speed: The speed of the drone in meters per second. The drone can go as slow as 0 meters per second and as
 * fast as 10 meters per second. faster speeds will drain the battery faster. Each meter per second will drain
 * the battery by 0.2% every time interval. The speed can only change by 1 meter per second every time interval.
 * 
 * - fishinView: A boolean value that indicates whether the fish is in view of the drone's camera.
 * 
 * - fishDepth: The depth of the fish in meters. The fish can go as deep as 100 meters and as shallow as 0 meters,
 * but it is known to stay at a depth of 50 meters. The drone must be within 1 meters of the fish to capture it on camera.
 * 
 * - fishSpeed: The speed of the fish in meters per second. The fish can go as slow as 0 meters per second and as
 * fast as 10 meters per second. It is known to swim at a speed of 1.5 meters per second.
 * 
 */

const app = express();
app.use(express.json());

let enableRandom = true;

class Drone {
    constructor() {
        this.depth = 0
        this.battery = 100
        this.speed = 0
        this.fishInView = false
        this.totalDepthChanged = 0
    }

    calculateRemainingBattery() {
        this.battery -= this.speed / 5
        if (this.battery < 0 ) {
            this.battery = 0
        }

        const speedBatteryDrain = this.battery
        return speedBatteryDrain - (this.totalDepthChanged / 5)
    }

    changeDepth(amount) {
        this.depth += amount
        if (this.depth < 0 ) {
            this.depth = 0
        }
        else if (this.depth > 100) {
            this.depth = 100
        }
        this.totalDepthChanged += Math.abs(amount)
    }

    changeSpeed(amount) {
        this.speed += amount
        if (this.speed < 0 ) {
            this.speed = 0
        }
        else if (this.speed > 10) {
            this.speed = 10
        }
    }

    checkFishInView() {
        this.fishInView = (Math.abs(this.depth - fish.depth) < 1 && Math.abs(this.speed - fish.speed) < 1)
        return this.fishInView
    }
}

class Fish {
    constructor() {
        this.depth = 50
        this.speed = 1.5
    }

    update() {
        this.changeDepth()
        this.changeSpeed()
    }

    changeDepth() {
        this.depth += Math.random() * 2 - 1
        if (this.depth < 0 ) {
            this.depth = 0
        }
        else if (this.depth > 100) {
            this.depth = 100
        }
    }

    changeSpeed() {
        this.speed += Math.random() - 0.5
        if (this.speed < 0 ) {
            this.speed = 0
        }
        else if (this.speed > 10) {
            this.speed = 10
        }
    }
}

const drone = new Drone()
const fish = new Fish()

app.get('/', function (req, res) {
    res.send("alive")
});

app.get('/disableFishMovement', function (req, res) {
    enableRandom = false
    res.status(200).json({message: "Fish movement disabled"})
});


app.get('/monitor', function (req, res) {
    if (enableRandom) {
        fish.update()
    }
    res.send(JSON.stringify({
        depth: drone.depth,
        battery: drone.calculateRemainingBattery(),
        speed: drone.speed,
        fishInView: drone.checkFishInView(),
        fishDepth: fish.depth,
        fishSpeed: fish.speed
    }));
});

app.put('/execute', function (req, res) {
    console.log("Got value changes: depth:" + req.body.depth + " - speed:" + req.body.speed)
    if (req.body) {
        console.log("Got value changes: depth:" + req.body.depth + " - speed:" + req.body.speed)
        drone.changeDepth(req.body.depth)
        drone.changeSpeed(req.body.speed)
    }
    res.send("ok")
});

app.get('/monitor_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            depth: {
                type: "number"
            },
            battery: {
                type: "number"
            },
            speed: {
                type: "number"
            },
            fishInView: {
                type: "boolean"
            },
            fishDepth: {
                type: "number"
            },
            fishSpeed: {
                type: "number"
            }
        }
    }));
});

app.get('/execute_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            depth: {
                type: "number"
            },
            speed: {
                type: "number"
            },
        }
    }));
});

app.get('/adaptation_options', function (req, res) {
    res.send(JSON.stringify({
        depth: {
            "start": -1.0,
            "stop": 1.0,
            "type": "continuous"
        },
        speed: {
            "start": -1.0,
            "stop": 1.0,
            "type": "continuous"
        }
    }));
});

app.get('/adaptation_options_schema', function (req, res) {
    res.send(JSON.stringify({
        type: "object",
        properties: {
            depth: {
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
            speed: {
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
    console.log(`upisas-demo-managed-system fish finder running on http://${HOST}:${PORT}`);
});
