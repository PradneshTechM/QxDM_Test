require('dotenv').config()
const process = require('process')
const path = require('path')
const fs = require('fs')

const NODE_ENV = process.env.NODE_ENV
const PORT = process.env.PORT !== undefined
  ? process.env.PORT
  : 2000
const ADDRESS = process.env.ADDRESS !== undefined
  ? process.env.ADDRESS
  : '0.0.0.0'
const DOMAIN = process.env.DOMAIN !== undefined
  ? process.env.DOMAIN
  : '0.0.0.0'
const PROTOCOL = NODE_ENV === 'development'
  ? 'http'
  : 'https'
const KEY_PATH = process.env.KEY_PATH
const CERT_PATH = process.env.CERT_PATH
const QUALCOMM_PATH = process.env.QUALCOMM_PATH
const QPM_USER = process.env.QPM_USER
const QPM_PASSWORD = process.env.QPM_PASSWORD

VARIABLES = [
  "KEY_PATH",
  "CERT_PATH",
  "STORAGE_PATH",
  "DB_NAME",
  "DB_HOST",
  "DB_USER",
  "DB_PASS",
  "DB_PORT",
  "DB_TABLE",
  "MEM_THRESHOLD",
  "MULTITHREADING",
  "AUTOMATION_DELETE_LOGS_AFTER_PARSING",
]

module.exports = {
  NODE_ENV, PORT, ADDRESS, DOMAIN, PROTOCOL, KEY_PATH, CERT_PATH, QUALCOMM_PATH, QPM_USER, QPM_PASSWORD
}

  ; (function createPythonEnv() {
    const src_path = path.join(__dirname, '..', '..', 'src')
    const env_path = path.join(src_path, '.env')
    let content = ""
    VARIABLES.forEach(key => {
      if (process.env[key]) {
        content += `${key}=${process.env[key]}\n`
      }
    })
    fs.writeFileSync(env_path, content)
  })();