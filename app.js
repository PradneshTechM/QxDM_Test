const express = require('express');
const fs = require('fs');
const cors = require('cors');
const socket = require('socket.io');
const logger = require('./utils/logger');
const config = require('./utils/config');
const path = require('path');
const http = require('http');
const https = require('https');

// Import the new Appium Manager
const appiumManager = require('./appium-manager');

const app = express();

let server;

process.on('uncaughtException', async (err) => {
    logger.error(`${new Date().toISOString()}: process error is: ${err.message}`);
    // Restart management if there's a relevant error
    if (err.message.toLowerCase().includes("5037") || err.message.toLowerCase().includes("android") || err.message.toLowerCase().includes("adb")) {
        await appiumManager.restartAll();
    }
    process.exit(1);
});

process.on('unhandledRejection', async (err) => {
    logger.error(`${new Date().toISOString()}: unhandledRejection error is: ${err.message}`);
    await appiumManager.restartAll();
    process.exit(1);
});

if (config.NODE_ENV === 'development') {
    server = http.createServer(app);
} else {
    const credentials = {
        cert: fs.readFileSync(path.resolve(__dirname + '/../stf-ssl-certs/fullchain.pem')),
        key: fs.readFileSync(path.resolve(__dirname + '/../stf-ssl-certs/private.pem'))
    };
    server = https.createServer(credentials, app);
}

const io = socket(server);

app.use(cors());
app.use(express.json());
app.use('/api', require('./routes/api')(io));

app.use((req, res, next) => {
    res.status(404).send({ error: 'unknown endpoint' });
});

// Initialize Appium management
async function initializeAppiumManagement() {
    await appiumManager.initialize();
    setInterval(() => appiumManager.manageDevices(), config.FREQUENCY * 1000);
}

// Clean up and start management
initializeAppiumManagement();

server.listen(config.PORT, config.ADDRESS, () => {
    logger.info(`Server listening on ${config.PROTOCOL}://${config.ADDRESS}:${config.PORT}`);
    logger.info(`Updating every ${config.FREQUENCY} seconds`);
}).on('error', (err) => {
    logger.error(`Server error: ${err}`);
    processutil.solveAddressInUse(config.PORT);
});
