const bodyParser = require('body-parser')
const express = require('express')
const fs = require('fs')
const cors = require('cors')
const socket = require('socket.io')
const appiumManager = require('./appium-manager')
const logger = require('./utils/logger')
const config = require('./utils/config')
const path = require('path')

const app = express()

// process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0 // REMOVE AFTER SSL CERT UPDATED

let server;

if (config.NODE_ENV === 'development') {
  const http = require('http')

  server = http.createServer(app)
} else {
  const https = require('https')

  const credentials = {
    cert: fs.readFileSync(path.resolve(__dirname+'../stf-ssl-certs/fullchain.pem')),
    key: fs.readFileSync(path.resolve(__dirname+'../stf-ssl-certs/private.pem'))
  }
  server = https.createServer(credentials, app)
}

const io = socket(server)

app.use(cors())
app.use(bodyParser.json())
app.use('/api', require('./routes/api')(io))

const unknownEndpoint = (req, res) => {
  res.status(404).send({ error: 'unknown endpoint' })
}

// handler of requests with unknown endpoint
app.use(unknownEndpoint)

// removes existing device-container map file
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
  setInterval(() => appiumManager.manage(), config.FREQUENCY * 1000)
}

cleanUpExistingServers().then(() => manageServers())

// listen for requests
server.listen(config.PORT, config.ADDRESS, function () {
  logger.info(`Appium Manager Server now listening for requests at ${config.PROTOCOL}://${config.ADDRESS}:${config.PORT}`)
  logger.info(`Appium Manager Server updating every ${config.FREQUENCY} seconds`)
})