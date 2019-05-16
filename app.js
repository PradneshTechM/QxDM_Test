const bodyParser = require('body-parser')
const express = require('express')
const appiumManager = require('./appium-manager')
const logger = require('./log')

const app = express()
const port = 4000
const address = '0.0.0.0'
const frequency = (process.argv[2] != null ? process.argv[2] : 10)

app.use(bodyParser.json())

app.use('/api', require('./routes/api'))

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
app.listen(port, address, function () {
  logger.info(`Appium Manager Server now listening for requests at ${address}:${port}`)
  logger.info(`Appium Manager Server updating every ${frequency} seconds`)
})

