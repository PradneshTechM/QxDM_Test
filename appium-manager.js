const Promise = require('bluebird')
const Docker = require('dockerode')
const fs = require('fs')
const logger = require('./utils/logger')
const adb = require('adbkit')
const config = require('./utils/config')
const adbutil = require('./utils/adbutil')

let client
try {
  client = adb.createClient({host: config.ADB_HOST,port: config.ADB_PORT})
} catch (err) {
  logger.error(`${new Date().toISOString()}: Appium Manager crashed with ${err}`)
  adbutil.restartProcess().then(() => {
    client = adb.createClient({host: config.ADB_HOST,port: config.ADB_PORT})
  })
}

const MAX_DEVICES = 15
const PORT_START = 4723
const PORT_END = PORT_START + MAX_DEVICES
const IMAGE_NAME = 'techm/appium'
const CONTAINER_PREFIX = 'appium'

const ANDROID_SDK_PATH_BIND = '/usr/lib/android-sdk'
const ANDROID_LIB_PATH_BIND = '/usr/lib/android/'
const CRYPTO_PATH_BIND = '/lib/x86_64-linux-gnu/libcrypto.so.1.0.0'

const DEVICE_CONTAINER_MAP_FILE_NAME = 'device_container_map.txt'

const docker = new Docker()
let servers = {}
let usedPorts = {}
let deviceToContainerMap = {}

module.exports = {
  manage: autoManage
  , getServerRequest: getServerRequest
  , getCapabilitiesRequest: getCapabilitiesRequest
  , deleteServerRequest: deleteServerRequest
  , removeExistingServers: removeExistingServers
  , getContainer: getContainer
}

/**
 * Automatically starts and stops Appium containers based upon device connection.
 * Upon start, removes any existing Appium containers.
 *
 * Warning: if you start/stop containers manually, this app will not know.
 */
function autoManage() {
  client.listDevices().then(devices => {
    let connectedDevices = devices.map(device => device.id)
    let containers = Object.keys(servers)
    // console.log('devices not connected: ' + difference(containers, connectedDevices))
    // console.log('no containers for: ' + difference(connectedDevices, containers))

    stopServers(containers, connectedDevices).then(() => 
      startServers(containers, connectedDevices)
    )
  })
}

/**
 * Stops and removes any existing containers.
 */
async function removeExistingServers() {
  for (let i = 1; i <= MAX_DEVICES; i++) {
    let containerName = `/${CONTAINER_PREFIX}_${i}`
    await stopServerWithName(containerName)
  }
}

/**
 * Stops and removes existing container with name
 * @param {string} containerName
 */
function stopServerWithName(containerName) {
  let promise = new Promise((resolve, reject) => {
    docker.listContainers({all: true}, (err, containers) => {
      containers.forEach(container => {
        if (container.Names.includes(containerName)) {
          //logger.info(`Trying to stop existing container: ${containerName}`)
          docker.getContainer(container.Id).remove({force: true})
          logger.info(`Stopped existing container: ${containerName}`)
        }
      })
    })
    resolve()
  }).catch(function(err) {
    logger.error(`Error while stopping existing container: ${containerName}\n${err.stack}`)
  })

  return promise
}

/**
 * Stops containers that do not have a connected device.
 * @param {Array<string>} containers the running containers
 * @param {Array<string>} connectedDevices the connected devices
 */
async function stopServers(containers, connectedDevices) {
  let diff = difference(containers, connectedDevices)
  for (let i = 0; i < diff.length; i++) {
    let serial = diff[i]
    await stopServer(serial)
  }
}

/**
 * Starts containers for connected devices that do not already have containers.
 * @param {Array<string>} containers the running containers
 * @param {Array<string>} connectedDevices the connected devices
 */
async function startServers(containers, connectedDevices) {
  let diff = difference(connectedDevices, containers)
  for (let i = 0; i < diff.length; i++) {
    let serial = diff[i]
    let availablePorts = getNextUnusedPort()
    let containerName = generateContainerName(availablePorts.port)
    await startServer(serial, containerName, availablePorts)
      .catch(err => {
        if(err.message.toLowerCase().includes("conflict")) {
          stopServer(serial).then(() => startServer(serial, containerName, availablePorts))
        }
      })
  }
}

/**
 * Returns elements in first list that are not in second list.
 * @param {Array<string>} listA the first list
 * @param {Array<string>} listB the second list
 */
function difference(listA, listB) {
  return listA.filter(x => !listB.includes(x))
}

/**
 * Stops and removes the running container associated with given serial number.
 * @param {string} serial the serial number of the device
 */
function stopServer(serial) {
  let promise = new Promise((resolve, reject) => {
    let containerName = servers[serial].containerName
    //logger.info(`Trying to stop container for: ${serial}`)
    docker.getContainer(containerName).remove({force: true})
    resolve()
  }).catch(err => {
    logger.error(`Error while stopping container: ${serial}\n${err.stack}`)
  })

  // Remove stopped container info and port used
  promise.then(() => {
    const { containerName, port, bootstrapPort } = servers[serial]
    logger.info(`Stopped container for: ${serial}, name: ${containerName}, ` +
                `port: ${port}, bootstrap port: ${bootstrapPort}`)
    delete usedPorts[port]
    delete servers[serial]
    removeFromMap(serial)
  })

  return promise
}

/**
 * Starts an Appium container for device with given serial number.
 * @param {string} serial the serial number of the device
 */
function startServer(serial, containerName, availablePorts) {
  const { port, bootstrapPort } = availablePorts
  let promise = new Promise((resolve, reject) => {
    //logger.info(`Trying to start container for: ${serial}`)
    docker.createContainer({
      Image: IMAGE_NAME
      , Env: [
        `DEVICE_NAME=${serial}`,
        `APPIUM_PORT=${port}`,
        `BOOTSTRAP_PORT=${bootstrapPort}`,
        'RELAXED_SECURITY=true'
      ]
      , HostConfig: {
        Binds: [
          `${ANDROID_SDK_PATH_BIND}:${ANDROID_SDK_PATH_BIND}`,
          `${ANDROID_LIB_PATH_BIND}:${ANDROID_LIB_PATH_BIND}`,
          `${CRYPTO_PATH_BIND}:${CRYPTO_PATH_BIND}`
        ],
        NetworkMode: 'host'
      }
      , name: containerName
    }).then(container => {
      container.start()
      resolve(container)
    }).catch(err => {
      logger.error(`Error while starting container: ${serial}\n${err.stack}`)
      reject(new Error(`Error while starting container: ${serial}\n${err.stack}`))
    })
  })

  // Save newly started container info and port used
  promise.then((container) => {
    logger.info(`Started container for: ${serial}, name: ${containerName}, ` +
                `port: ${port}, bootstrap port: ${bootstrapPort}`)
    servers[serial] = { container, containerName, port, bootstrapPort }
    usedPorts[port] = true
    addToMap(serial, containerName)
  })

  return promise
}

function addToMap(device, containerName) {
  if (!deviceToContainerMap[device]) {
    deviceToContainerMap[device] = containerName
    saveMapToFile(deviceToContainerMap)
  } 
}

function removeFromMap(device) {
  if (deviceToContainerMap[device]) {
    delete deviceToContainerMap[device]
    saveMapToFile(deviceToContainerMap)
  }
}

function saveMapToFile(mapping) {
  const dataJSON = JSON.stringify(mapping)
  fs.writeFileSync(DEVICE_CONTAINER_MAP_FILE_NAME, dataJSON)
}

/**
 * Returns next available unused ports.
 * @return {number, number} the port and bootstrap port.
 * @throws if no unused ports are available
 */
function getNextUnusedPort() {
  for (let port = PORT_START; port < PORT_END; port++) {
    if (!usedPorts.hasOwnProperty(port)) {
      return {
        port,
        bootstrapPort: port + MAX_DEVICES
      }
    }
  }
  throw('MAX_DEVICE limit reached: no unused ports available')
}

/**
 * Returns a container name based upon given port number.
 * @param {number} port the main Appium port
 */
function generateContainerName(port) {
  return CONTAINER_PREFIX + '_' + (port - PORT_START + 1)
}

/**
 * Returns Appium server information for given device serial
 * @param {string} serial the serial number of the device
 */
async function getServerRequest(serial) {
  try {
    const devices = await client.listDevices()
    const match = devices.find(device => device.id === serial)
    const device = (match && match.type === 'device') ? match : null
    let response = {}
    if (device) {
      if (servers[serial] && servers[serial].port) {  // already running server
        response.port = servers[serial].port
        response.status = 200
        response.statusText = 'Found device with given serial number'
      } else {  // not running yet, start
        response.status = 400
        response.statusText = 'Appium server not started yet'
        startServer(serial)
      }
    } else {
      response.statusText = 'No device with given serial number'
      response.status = 404
    }
    return response
  } catch (err) {
    logger.error(err)
  }
}

/**
 * Returns Appium server capabilities for given device serial
 * @param {string} serial the serial number of the device
 */
async function getCapabilitiesRequest(serial) {
  try {
    const devices = await client.listDevices()
    const match = devices.find(device => device.id === serial)
    const device = (match && match.type === 'device') ? match : null
    let response = {}
    if (device) {
      if (servers[serial] && servers[serial].port) {  // already running server
        response.capabilities = {
          'deviceName': serial,
          'udid': serial,
          'appPackage': 'com.android.settings',
          'platformName': 'Android',
          'appActivity': 'com.android.settings.Settings'
        }
        response.status = 200
        response.statusText = 'Found device with given serial number'
      } else {  // not running yet, start
        response.status = 400
        response.statusText = 'Appium server not started yet'
        startServer(serial)
      }
    } else {
      response.statusText = 'No device with given serial number'
      response.status = 404
    }
    return response
  } catch (err) {
    logger.error(err)
  }
}

/**
 * Stops Appium server for given device serial.
 * @param {string} serial the serial number of the device
 */
async function deleteServerRequest(serial) {
  try {
    const devices = await client.listDevices()
    const match = devices.find(device => device.id === serial)
    const device = (match && match.type === 'device') ? match : null
    let response = {}
    if (device) {
      // does device with serial have running Appium server?
      if (servers[serial]) {
        // already running server
        response.port = servers[serial].port
        response.status = 200
        response.statusText = 'Restarted server for device with given serial number'
        stopServers([serial], [])
      } else {
        // not running yet, start
        response.status = 400
        response.statusText = 'Server is not started for device with given serial number'
        startServer(serial)
      }
    } else {
      response.statusText = 'No device with given serial number'
      response.status = 404
    }
    return response
  } catch (err) {
    logger.error(err)
  }
}

/**
 * Returns the docker container for given serial number.
 * @param {string} serial the serial number of the device
 */
function getContainer(serial) {
  return servers[serial] ? servers[serial].container : null
}
