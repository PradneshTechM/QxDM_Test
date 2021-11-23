require('dotenv').config()
const process = require('process')

const NODE_ENV = process.env.NODE_ENV
const PORT = process.env.PORT !== undefined
  ? process.env.PORT
  : 6000
const ADDRESS = process.env.ADDRESS !== undefined
  ? process.env.ADDRESS
  : '0.0.0.0'
const DOMAIN = process.env.DOMAIN !== undefined
  ? process.env.DOMAIN
  : '0.0.0.0'
const PROTOCOL = NODE_ENV === 'development'
  ? 'http'
  : 'https'

module.exports = {
  NODE_ENV, PORT, ADDRESS, DOMAIN, PROTOCOL
}
