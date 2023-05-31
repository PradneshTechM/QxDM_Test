const app = require('./app')
const io = require('socket.io-client')
const logger = require('./utils/logger')
const config = require('./utils/config')

let server

if (config.NODE_ENV === 'development') {
  const http = require('http')

  server = http.createServer(app)
} else {
  const https = require('https')
  const fs = require('fs')

  const credentials = {
    cert: fs.readFileSync('/home/techm/tmdc/stf-ssl-certs/ssl-bundle.crt'),
    key: fs.readFileSync('/home/techm/tmdc/stf-ssl-certs/server.key'),
  }
  server = https.createServer(credentials, app)
}

server.listen(config.PORT, config.ADDRESS, () => {
  logger.info(`qConnect server now listening for requests at ${config.PROTOCOL}://${config.ADDRESS}:${config.PORT}`)
})

const socket = io('http://localhost:6001')
app.set('socketio', socket)

socket.on("QCAT_parse_done", (result) => {
  logger.info('QCAT_parse_done: ' + result.data.status)
})

// listen for SIGINT, SIGTERM on windows: https://stackoverflow.com/a/14861513
if (process.platform === 'win32') {
  const rl = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  })

  rl.on('SIGINT', () => process.emit('SIGINT'))
  rl.on('SIGTERM', () => process.emit('SIGTERM'))
}

process.on('SIGINT', stopHandler)
process.on('SIGTERM', stopHandler)

function stopHandler() {
  logger.info('Stopping...')

  // send event to listening python process to kill child processes
  socket.emit('stop_all', null, (res) => {
    server.close(() => process.exit(0))
  })
  
  setTimeout(() => process.exit(0), 3000)
}
