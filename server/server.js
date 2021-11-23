const app = require('./app')
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
