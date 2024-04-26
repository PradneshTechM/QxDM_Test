const { remote } = require('webdriverio');
const appiumManager = require('./appium-manager');
const adb = require('adbkit');
const logger = require('./utils/logger');
const client = adb.createClient();

async function validateDeviceServerMatching() {
    appiumManager.initialize();
    console.log("Initializing Appium Manager...");

    // Wait for servers to stabilize
    await new Promise(resolve => setTimeout(resolve, 10000));

    // Retrieve current server and device details from Appium Manager
    const managedServers = appiumManager.getCurrentServerDetails();
    const connectedDevices = await client.listDevices();

    // Check if the number of managed servers matches the number of connected devices
    if (managedServers.length !== connectedDevices.length) {
        logger.error(`Mismatch! Managed servers: ${managedServers.length}, Connected devices: ${connectedDevices.length}`);
        return false; // Indicates a mismatch
    }

    // Further validate that every managed server corresponds to a connected device
    const managedDeviceIds = managedServers.map(server => server.udid);
    const connectedDeviceIds = connectedDevices.map(device => device.id);

    // Check if every device ID from managed servers is present in the list of connected device IDs
    const allDevicesMatched = managedDeviceIds.every(id => connectedDeviceIds.includes(id));
    if (!allDevicesMatched) {
        logger.error('Some managed servers do not correspond to currently connected devices.');
        return false;
    }

    // All checks passed, now print UDID and port of each device
    logger.info('All managed servers correctly correspond to connected devices.');
    managedServers.forEach(server => {
        console.log(`Device UDID: ${server.udid}, Server Port: ${server.port}`);
    });
    return true; // All checks passed
}

async function main() {
    try {
        const isValid = await validateDeviceServerMatching();
        if (!isValid) {
            throw new Error('Device and server validation failed.');
        }

        // Continue with additional testing or operations...
    } catch (error) {
        logger.error(`Failed during validation or subsequent operations: ${error}`);
    }
}

main();
