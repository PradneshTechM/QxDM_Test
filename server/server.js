const app = require('./app')
const io = require('socket.io-client')
const logger = require('./utils/logger')
const path = require('path')
const config = require('./utils/config')

let server

if (config.NODE_ENV === 'development') {
  const http = require('http')

  server = http.createServer(app)
} else {
  const https = require('https')
  const fs = require('fs')

  const credentials = {
    cert: fs.readFileSync(path.resolve(config.CERT_PATH)),
    key: fs.readFileSync(path.resolve(config.KEY_PATH))
  }
  server = https.createServer(credentials, app)
}

const serverAddr = config.NODE_ENV === 'development' ? "localhost" : config.ADDRESS
server.listen(config.PORT, serverAddr, () => {
  logger.info(`qConnect server now listening for requests at ${config.PROTOCOL}://${serverAddr}:${config.PORT}`)
})

const socketAddr = config.NODE_ENV == 'development' ? `http://localhost:6001` : `${config.PROTOCOL}://${config.ADDRESS}:6001`
const socket = io(socketAddr)
app.set('socketio', socket)

socket.on("QCAT_parse_done", (result) => {
  logger.info('QCAT_parse_done: ' + JSON.stringify(result.data, null, 2))
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
