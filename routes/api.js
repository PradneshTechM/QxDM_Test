const express = require('express')
const router = express.Router()
const appiumManager = require('../appium-manager')
const { PassThrough } = require('stream')
const util = require('util')
const logger = require('../log')
const TAIL_LOG_LINES = 1000
const DATA_REFRESH_RATE = 50 // in ms

module.exports = (io, address) => {
  const DOMAIN = `http://${address}`

  /**
   * Get running Appium server information for given device serial
   */
  router.get('/servers/:serial', async (req, res) => {
    const serial = req.params.serial
    // logger.info('GET request for serial: %s', serial)
    try {
      const result = await appiumManager.getServerRequest(serial)
      let response = {
        type: 'GET',
        status: result && result.status || 400,
        port: result && result.port || null,
        statusText: result && result.statusText || null,
        serial: serial,
        URL: result && result.status == 200 ? `${DOMAIN}:${result.port}/wd/hub` : null
      }
      // logger.info({
      //   message: `${response.status} - ${response.statusText}, URL: ${response.URL}`,
      //   response: response
      // })
      res.send(response)
    } catch (err) {
      logger.error(`Error on GET request for serial: ${serial}\n${err.stack}`)
    }
  })

  /**
   * Restart running Appium server for given device serial
   */
  router.delete('/servers/:serial', async (req, res) => {
    const serial = req.params.serial
    logger.info('DELETE request for serial: %s', serial)
    try {
      const result = await appiumManager.deleteServerRequest(serial)
      let response = {
        type: 'DELETE',
        status: result.status,
        statusText: result.statusText,
        serial: serial
      }
      logger.info({
        message: `${result.status} - ${result.statusText}`,
        response: response
      })
      res.send(response)
    } catch (err) {
      logger.error(`Error on DELETE request for serial: ${serial}\n${err.stack}`)
    }
  })

  /**
   * Handles log requests
   */
  io.on('connection', (socket) => {
    console.log('socket connected: ', socket.id)

    socket.on('disconnect', () => {
      console.log('socket disconnected: ', socket.id)
    })

    socket.on('request logs', (serial) => {
      const logStream = new PassThrough()

      let data = []
      logStream.on('data', (chunk) => {
//console.log(util.inspect(chunk.toString('utf8').replace(/\u001b\[\w{1,3}/g, '')))
        // remove muxed in header
        data.push(chunk.toString('utf8').replace(/\u001b\[\w{1,3}/g, '')) 
      })

      const interval = setInterval(() => {
        if (data.length > 0) {
          io.to(socket.id).emit('log message', { data, device: serial })
          data = []
        }
      }, DATA_REFRESH_RATE)

      const container = appiumManager.getContainer(serial)
      if (container) {
        container.logs({
          follow: true,
          stdout: true,
          stderr: true,
          tail: TAIL_LOG_LINES
        }, (err, stream) => {
          if (err) {
            return logger.error(err.message)
          }
          container.modem.demuxStream(stream, logStream, logStream)
          stream.on('end', () => {
            logStream.end()
          })

          socket.once('stop', (stopSerial) => {
            logger.info(`socket.id: ${socket.id} emitted 'stop'`)
            if (serial === stopSerial) {
              stream.destroy()
              clearInterval(interval)
            }
          })
        })
      }
    })
  })

  return router
}
