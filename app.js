const bodyParser = require('body-parser')
const express = require('express')
const fs = require('fs')
const http = require('http')
const https = require('https')
const cors = require('cors')
const socket = require('socket.io')
const appiumManager = require('./appium-manager')
const logger = require('./log')

const app = express()
const port = 4000
const address = '0.0.0.0'
const frequency = (process.argv[2] != null ? process.argv[2] : 2)

// process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0 // REMOVE AFTER SSL CERT UPDATED

const credentials = {
  cert: fs.readFileSync('/etc/nginx/SSL/ssl-bundle.crt'),
  key: fs.readFileSync('/etc/nginx/SSL/server.key')
}

const server = https.createServer(credentials, app)
// const server = http.createServer(app)
const io = socket(server)

app.use(cors())
app.use(bodyParser.json())
app.use('/api', require('./routes/api')(io))

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
  logger.info(`Appium Manager Server now listening for requests at https://${address}:${port}`)
  logger.info(`Appium Manager Server updating every ${frequency} seconds`)
})

