const bodyParser = require('body-parser')
const express = require('express')
const fs = require('fs')
const http = require('http')
const cors = require('cors')
const socket = require('socket.io')
const appiumManager = require('./appium-manager')
const logger = require('./log')

const app = express()
const port = 4000
const server = http.createServer(app)
const io = socket(server)

if (!process.argv[2]) {
  return logger.error('No address passed in')
}
const address = process.argv[2]

if (!process.argv[3]) {
  logger.info('No frequency passed in. Default value used.')
}
const frequency = (process.argv[3] != null ? process.argv[3] : 2)

app.use(cors())
app.use(bodyParser.json())
app.use('/api', require('./routes/api')(io, address))

fs.stat('device_container_map.txt', (err, stats) => {
  if (err) {
    return console.log(err);
  }
  fs.unlinkSync('device_container_map.txt')
})

// removes any existing Appium server on startup
async function cleanUpExistingServers() {
  await setTimeout(() => appiumManager.removeExistingServers(), 500)
}

// manages Appium server every frequency seconds
function manageServers() {
  setInterval(() => appiumManager.manage(), frequency * 1000)
}

cleanUpExistingServers().then(() => manageServers())

// listen for requests
server.listen(port, address, function () {
  logger.info(`Appium Manager Server now listening for requests at http://${address}:${port}`)
  logger.info(`Appium Manager Server updating every ${frequency} seconds`)
})

