const express = require('express')
const router = express.Router()
const appiumManager = require('../appium-manager')
const logger = require('../log')

const DOMAIN = `http://atas.techmlab.com`

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
    res.status(result.status).send(response)
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
    res.status(result.status).send(response)
  }).catch(err => {
    logger.error(`Error on DELETE request for serial: ${serial}\n${err.stack}`)
  })
})

module.exports = router