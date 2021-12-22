const api = require('./api')
const basicInfo = require('./basicInfo')
const components = require('./components')
const servers = require('./servers')
const tags = require('./tags')

module.exports = {
  ...api,
  ...basicInfo,
  ...components,
  ...servers,
  ...tags,
}