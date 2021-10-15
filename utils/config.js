require('dotenv').config()

const NODE_ENV = process.env.NODE_ENV
const PORT = process.env.PORT != undefined
  ? process.env.PORT
  : 4000
const ADDRESS = process.env.ADDRESS != undefined
  ? process.env.ADDRESS
  : '0.0.0.0'
const DOMAIN = process.env.DOMAIN != undefined
  ? process.env.DOMAIN
  : '0.0.0.0'
const FREQUENCY = process.env.FREQUENCY != undefined
  ? process.env.FREQUENCY
  : 2
const PROTOCOL = NODE_ENV === 'development'
  ? 'http'
  : 'https'
const STF_LOCAL_API_PORT = 7106

const SWAGGER_URL = NODE_ENV === 'production'
  ? `${PROTOCOL}://${DOMAIN}/api/v1/swagger.json`
  : `${PROTOCOL}://${DOMAIN}:${STF_LOCAL_API_PORT}/api/v1/swagger.json`
const APPIUM_SERVER = `${PROTOCOL}://${DOMAIN}:4000/api`

module.exports = {
  NODE_ENV, PORT, ADDRESS, DOMAIN, FREQUENCY, PROTOCOL, SWAGGER_URL, APPIUM_SERVER
}
