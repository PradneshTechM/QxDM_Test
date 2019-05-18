const Promise = require('bluebird')
const Docker = require('dockerode')
const logger = require('./log')
const adb = require('adbkit')
const client = adb.createClient()

const MAX_DEVICES = 6
const PORT_START = 4723
const PORT_END = PORT_START + MAX_DEVICES
const CONTAINER_PREFIX = 'appium'

const ADB_PATH_BIND = '/home/techm/Android/Sdk'
const CRYPTO_PATH_BIND = '/lib/x86_64-linux-gnu/libcrypto.so.1.0.0'

const docker = new Docker()
let servers = {}
let usedPorts = {}

module.exports = {
  manage: autoManage
  , getServerRequest: getServerRequest
  , deleteServerRequest: deleteServerRequest
  , removeExistingServers: removeExistingServers
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

    stopServers(containers, connectedDevices)
    startServers(containers, connectedDevices)
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
    let containerName = servers[serial].containerName
    let port = servers[serial].port
    let bootstrapPort = servers[serial].bootstrapPort
    logger.info(`Stopped container for: ${serial}, name: ${containerName}, ` +
                `port: ${port}, bootstrap port: ${bootstrapPort}`)
    delete usedPorts[port]
    delete servers[serial]
  })
  
  return promise
}

/**
 * Starts an Appium container for device with given serial number.
 * @param {string} serial the serial number of the device
 */
function startServer(serial, containerName, availablePorts) {
  let port = availablePorts.port
  let bootstrapPort = availablePorts.bootstrapPort
  let promise = new Promise((resolve, reject) => {
    //logger.info(`Trying to start container for: ${serial}`)
    docker.createContainer({
      Image: 'appium/appium:local'
      , Env: [
        `DEVICE_NAME=${serial}`,
        `APPIUM_PORT=${port}`,
        `BOOTSTRAP_PORT=${bootstrapPort}`
      ]
      , HostConfig: {
        Binds: [
          `${ADB_PATH_BIND}:${ADB_PATH_BIND}`,
          `${CRYPTO_PATH_BIND}:${CRYPTO_PATH_BIND}`
        ],
        NetworkMode: 'host'
      }
      , name: containerName
    }).then(container => {
      container.start()
      resolve()
    }).catch(err => {
      logger.error(`Error while starting container: ${serial}\n${err.stack}`)
    })
  })
  
  // Save newly started container info and port used
  promise.then(() => {
    logger.info(`Started container for: ${serial}, name: ${containerName}, ` +
                `port: ${port}, bootstrap port: ${bootstrapPort}`)
    servers[serial] = {
      containerName : containerName,
      port: port,
      bootstrapPort: bootstrapPort
    }
    usedPorts[port] = bootstrapPort
  })

  return promise
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
        port: port,
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
function getServerRequest(serial) {
  return client.listDevices()
    // is device with serial connected?
    .then(devices => {
      let match = devices.find(device => device.id === serial)
      return (match && match.type === 'device') ? match : null
    }).then(device => {
      let response = {
        status: null,
        statusText: '',
        port: null
      }
      if (device) {
        // does device with serial have running Appium server?
        if (servers[serial]) {
          // already running server
          response.port = servers[serial].port
          response.status = 200
          response.statusText = 'Found device with given serial number'
        } else {
          // not running yet, start
          response.status = 400
          response.statusText = 'Appium server not started yet'
          // startServer(serial)
        }
      } else {
        response.statusText = 'No device with given serial number'
        response.status = 404
      }
      return response
    }).catch(err => logger.error(err))
}

/**
 * Stops Appium server for given device serial.
 * @param {string} serial the serial number of the device
 */
function deleteServerRequest(serial) {
  return client.listDevices()
    // is device with serial connected?
    .then(devices => {
      let match = devices.find(device => device.id === serial)
      return (match && match.type === 'device') ? match : null
    }).then(device => {
      let response = {
        status: null,
        statusText: '',
        port: null
      }
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
          // startServer(serial)
        }
      } else {
        response.statusText = 'No device with given serial number'
        response.status = 404
      }
      return response
    }).catch(err => logger.error(err))
}