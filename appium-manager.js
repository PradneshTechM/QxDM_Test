const { spawn } = require('child_process');
const adb = require('adbkit');
const logger = require('./utils/logger');
const config = require('./utils/config');
const PORT_START = 4723;
const MAX_DEVICES = 15;
let servers = {};  // Tracks server, port, and device info
let usedPorts = new Set();

const client = adb.createClient({ host: config.ADB_HOST, port: config.ADB_PORT });

function getNextAvailablePort() {
    for (let port = PORT_START; port < PORT_START + MAX_DEVICES * 2; port += 2) {
        if (!usedPorts.has(port)) {
            usedPorts.add(port);
            return port;
        }
    }
    throw new Error('No available ports');
}

async function startServer(device) {
    const port = getNextAvailablePort();
    const appiumServer = spawn('appium', [`--port=${port}`, '--session-override'], { detached: true, shell: true });

    appiumServer.stdout.on('data', data => logger.info(`Appium-${device.id}: ${data.toString()}`));
    appiumServer.stderr.on('data', data => logger.error(`Appium-${device.id} Error: ${data.toString()}`));

    // appiumServer.on('close', code => {
    //     logger.info(`Appium server for device ${device.id} stopped with code ${code}`);
    //     usedPorts.delete(port);
    //     delete servers[device.id];
    // });

    servers[device.id] = {
        process: appiumServer,
        port: port,
        deviceDetails: {
            name: device.model || device.id,  // Using device model or ID as name
            platformVersion: device.version,  // Assuming 'version' is available in device info
            udid: device.id
        }
    };
}

async function manageDevices() {
    const devices = await client.listDevices();
    devices.forEach(async device => {
        if (!servers.hasOwnProperty(device.id)) {
            await startServer(device);
        }
    });

    // Check and stop servers for disconnected devices
    Object.keys(servers).forEach(serverDeviceId => {
        if (!devices.find(device => device.id === serverDeviceId)) {
            stopServer(serverDeviceId);
        }
    });
}

function initialize() {
    manageDevices();  // Initial call to setup devices immediately
    setInterval(manageDevices, 10000);  // Check and manage devices every 10 seconds
}


function stopServer(deviceId) {
    const server = servers[deviceId];
    if (server) {
        server.process.kill('SIGINT');
        logger.info(`Stopped Appium server for device ${deviceId}`);
        usedPorts.delete(server.port);
        delete servers[deviceId];
    }
}

function getCurrentServerDetails() {
    return Object.entries(servers).map(([deviceId, { port, deviceDetails }]) => ({
        deviceId,
        port,
        deviceName: deviceDetails.name,
        platformVersion: deviceDetails.platformVersion,
        udid: deviceDetails.udid
    }));
}

async function deleteServerRequest(serial) {
  await stopServer(serial);
  return {
    status: 200,
    statusText: 'Server stopped',
    serial: serial
  };
}

async function getCapabilitiesRequest(serial) {
  const serverDetails = getCurrentServerDetails().find(s => s.deviceId === serial);
  if (serverDetails) {
    return {
      status: 200,
      capabilities: serverDetails.deviceDetails,
      statusText: 'Capabilities fetched'
    };
  } else {
    return {
      status: 404,
      statusText: 'No server for this device'
    };
  }
}


module.exports = { initialize, stopServer, getCurrentServerDetails, deleteServerRequest, getCapabilitiesRequest};
