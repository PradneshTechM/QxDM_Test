const config = require('../utils/config')

module.exports = {
  servers: [
    {
      url: `http://localhost:${config.PORT}`,
      description: 'Local server',
    }
  ]
}