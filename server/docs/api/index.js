const connectDiag = require('./connect-diag')
const disconnectDiag = require('./disconnect-diag')
const startLog = require('./start-log')
const stopLog = require('./stop-log')
const processLog = require('./process-log')
const getLog = require('./get-log')
const connectAT = require('./connect-AT')
const disconnectAT = require('./disconnect-AT')
const sendAT = require('./send-AT')

module.exports = {
  paths: {
    '/api/diag': {
      ...connectDiag,
    },
    '/api/diag/{id}': {
      ...disconnectDiag,
    },
    '/api/logs': {
      ...startLog,
    },
    '/api/logs/{log_id}': {
      ...stopLog,
    },
    '/api/logs/{log_id}/process': {
      ...processLog,
      ...getLog,
    },
    '/api/AT': {
      ...connectAT,
    },
    '/api/AT/{id}': {
      ...disconnectAT,
      ...sendAT,
    },
  }
}