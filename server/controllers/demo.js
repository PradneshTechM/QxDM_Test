const demoRouter = require('express').Router()
const logger = require('../utils/logger')

const runPythonPromise = (testcase) => {
  let pythonScriptPath
  switch(testcase) {
  case 'tc1':
    pythonScriptPath = '../../src/run_tc1_lte_latch_quts.py'
    break
  case 'tc2':
    pythonScriptPath = '../../src/run_tc2_VoLTE_call_quts.py'
    break
  default:
    pythonScriptPath = null
  }

  return new Promise((resolve, reject) => {
    const { spawn } = require('child_process')
    const pythonProgram = spawn('python', pythonScriptPath)

    pythonProgram.stdout.on('data', (data) => {
      resolve(data)
    })

    pythonProgram.stderr.on('data', (data) => {
      reject(data)
    })
  })
}

demoRouter.post('/tc1', async (request, response) => {
  try {
    const output = await runPythonPromise('tc1')
    logger.info(output)
    response.end(output)
  } catch (error) {
    logger.error(error)
    response.end(error)
  }
})

demoRouter.post('/tc2', async (request, response) => {
  try {
    const output = await runPythonPromise('tc2')
    logger.info(output)
    response.end(output)
  } catch (error) {
    logger.error(error)
    response.end(error)
  }
})

module.exports = demoRouter
