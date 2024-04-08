const os = require('os');
const config = require('./config');

module.exports.getAvailableMemory = () => {
  let freeMemory
  try {
    freeMemory = os.freemem()
  } catch (e) {
    freeMemory = config.FALL_BACK_FREE_MEM
  }
  return freeMemory
}

module.exports.sleep = async (duration = 1000) => {
  return new Promise(resolve => {
    setTimeout(resolve, duration)
  })
}