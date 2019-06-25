const express = require('express')
const router = express.Router()
const appiumManager = require('../appium-manager')
const { PassThrough } = require('stream')
const logger = require('../log')

const DOMAIN = `http://atas.techmlab.com`

module.exports = (io) => {
  /**
   * Get running Appium server information for given device serial
   */
  router.get('/servers/:serial', function(req, res) {
    const serial = req.params.serial
    logger.info('GET request for serial: %s', serial)
    appiumManager.getServerRequest(serial).then(result => {
      let response = {
        type: 'GET',
        status: result.status,
        port: result.port,
        statusText: result.statusText,
        serial: req.params.serial,
        URL: result.status == 200 ? `${DOMAIN}:${result.port}/wd/hub` : null
      }
      logger.info({
        message: `${response.status} - ${response.statusText}, URL: ${response.URL}`,
        response: response
      })
      res.send(response)
    }).catch(err => {
      logger.error(`Error on GET request for serial: ${serial}\n${err.stack}`)
    })
  })

  /**
   * Restart running Appium server for given device serial
   */
  router.delete('/servers/:serial', function(req, res) {
    const serial = req.params.serial
    logger.info('DELETE request for serial: %s', serial)
    appiumManager.deleteServerRequest(serial).then(result => {
      let response = {
        type: 'DELETE',
        status: result.status,
        // port: result.port,
        statusText: result.statusText,
        serial: req.params.serial,
        // URL: 'placeholder'
      }
      logger.info({
        message: `${result.status} - ${result.statusText}`,
        response: response
      })
      res.send(response)
    }).catch(err => {
      logger.error(`Error on DELETE request for serial: ${serial}\n${err.stack}`)
    })
  })

  /**
   * Handles log requests
   */
  io.on('connection', (socket) => {
    console.log('socket connected: ', socket.id)

    socket.on('disconnect', () => {
      console.log('socket disconnected')
    })

    socket.on('request logs', (serial) => {
      const logStream = new PassThrough()

      let data = []
      logStream.on('data', (chunk) => {
        data.push(chunk.toString('utf8').replace(/\u001b\[\w+/g, '')) // remove muxed in header
      })

      const interval = setInterval(() => {
        if (data.length > 0) {
          io.to(socket.id).emit('log message', { data: data, device: serial })
          data = []
        }
      }, 100)

      const container = appiumManager.getContainer(serial)
      container.logs({
        follow: true,
        stdout: true,
        stderr: true
      }, (err, stream) => {
        if (err) {
          return logger.error(err.message)
        }
        container.modem.demuxStream(stream, logStream, logStream)
        stream.on('end', () => {
          logStream.end()
        })

        socket.on('stop', (stopSerial) => {
          if (serial === stopSerial) {
            stream.destroy()
            clearInterval(interval)
          }
        })
      })
    })
  })

  return router
}
