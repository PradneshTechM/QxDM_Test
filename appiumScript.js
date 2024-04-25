const { remote } = require('webdriverio');
const appiumManager = require('./appium-manager');
const logger = require('./utils/logger');

async function runTest(deviceConfig) {
    const client = await remote({
        path: '/wd/hub',
        port: deviceConfig.port,
        capabilities: {
            platformName: "Android",
            deviceName: deviceConfig.deviceName,
            udid: deviceConfig.udid,
            platformVersion: deviceConfig.platformVersion,
            appPackage: "com.cooingdv.rcfpv",
            appActivity: "com.cooingdv.rcfpv.activity.MainActivity",
            noReset: true,
            autoAcceptAlerts: true
        }
    });

    try {
        console.log(`Running test on device: ${deviceConfig.deviceName}`);
        // Insert your test actions here, e.g., navigating the app or checking UI elements.
        console.log(`Test passed on device ${deviceConfig.deviceName}`);
    } catch (error) {
        console.error(`Test failed on device ${deviceConfig.deviceName}: ${error}`);
    } finally {
        await client.deleteSession();
    }
}

async function main() {
    try {
        // Initialize the Appium Manager to manage Appium servers
        appiumManager.initialize();
        console.log("Appium Manager is initializing. Waiting for servers to be ready...");

        // Wait for the server management to stabilize
        await new Promise(resolve => setTimeout(resolve, 10000)); // 10-second delay for server setup

        // Retrieve current server and device details from Appium Manager
        const devices = appiumManager.getCurrentServerDetails();
        for (let device of devices) {
            await runTest({
                deviceName: device.deviceName,
                port: device.port,
                udid: device.udid,
                platformVersion: device.platformVersion
            });
        }
    } catch (error) {
        logger.error(`Failed to run tests: ${error}`);
    }
}

main();
