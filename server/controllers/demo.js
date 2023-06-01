const demoRouter = require('express').Router()
const path = require('path')
const { spawn } = require('child_process')
const crypto = require('crypto')
const AdmZip = require('adm-zip')
const logger = require('../utils/logger')
const config = require('../utils/config')


const generateUUID = () => {
  return crypto.randomUUID()
}

const generateShortId = (bytes) => {
  return crypto.randomBytes(bytes).toString('hex')
}

const pythonServicePath = path.join(__dirname, '..', '..', 'src', 'qConnect_service.py')

const defaults = { cwd: path.parse(pythonServicePath).dir }
const pythonProgram = spawn('python', [pythonServicePath, "--env", config.NODE_ENV], defaults)

pythonProgram.stdout.on('data', (data) => {
  logger.info('python_service: ' + data.toString())
})

pythonProgram.stderr.on('data', (data) => {
  logger.info('python_service: ' + data.toString())
})


demoRouter.post('/diag', (request, response) => {
  // starts logging
  // socket.io usage: https://stackoverflow.com/a/43685951
  if (request.body.serial === undefined) {
    return response.status(400).send({ error : 'missing serial' })
  }
  const data = {
    id: generateShortId(8),
    serial: request.body.serial,
    user: request.body.user? request.body.user: {
      name: "unknown",
      email: "unknown"
    },
    appUrl: request.body.appUrl,
    device: request.body.device ? request.body.device: {}
  }
  if(request.body.mask) {
    data.mask = request.body.mask
  }

  const socket = request.app.get('socketio')
  socket.emit('QUTS_diag_connect', data, (res) => {
    console.log(res)
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
  })
})

demoRouter.delete('/diag/:id', (request, response) => {
  console.log(request.body)
  const data = {
    id: request.params.id,
  }

  const socket = request.app.get('socketio')

  socket.emit('QUTS_diag_disconnect', data, (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
  })
})

demoRouter.post('/logs', (request, response) => {
  // starts logging
  if (request.body.id === undefined) {
    return response.status(400).send({ error : 'missing id' })
  }
  console.log(request.body)
  const data = {
    id: request.body.id,
    log_id: generateShortId(4),
  }

  const socket = request.app.get('socketio')

  socket.emit('QUTS_log_start', data, (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
  })
})

demoRouter.delete('/logs/:log_id', (request, response) => {
  // stops logging
  console.log(request.body)
  const data = {
    log_id: request.params.log_id,
  }
  
  const socket = request.app.get('socketio')
  
  socket.emit('QUTS_log_stop', data, async (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
    
    setTimeout(() => autoParse(request, response), 100)
  })
})

async function autoParse(request, response) {
  logger.info("Auto parse")
  await new Promise(resolve => setTimeout(resolve, 100))
  
  const data = {
    log_id: request.params.log_id,
  }
  
  const socket = request.app.get('socketio')
  
  socket.emit('QCAT_parse_all', data, (res) => {
    if (res.error) {
      logger.error(`Could not parse ${res.error}`)
    } else {
      logger.info(res.data.status)
    }
  })
}

demoRouter.post('/logs/:log_id/process', (request, response) => {
  // processes log
  console.log(request.body)
  if (request.body.test_case === undefined) {
    return response.status(400).send({ error : 'missing test_case' })
  }
  const data = {
    log_id: request.params.log_id,
    test_case: request.body.test_case
  }

  const socket = request.app.get('socketio')
  socket.emit('QCAT_process', data, (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
  })
})

demoRouter.get('/logs/:log_id/process', (request, response) => {
  // gets processed log
  console.log(request.body)
  const data = {
    log_id: request.params.log_id,
  }

  const socket = request.app.get('socketio')
  socket.emit('get_log', data, (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    const { filepath, test_case } = res.data
    if (test_case === 'TC1') {
      response.download(filepath)
    } else {
      const zip = new AdmZip()
      zip.addLocalFile(filepath)
      zip.addLocalFile(filepath.replace('MO.csv', 'MT.csv'))

      const zipFileContents = zip.toBuffer()
      const fileName = 'tc2_results.zip'
      const fileType = 'application/zip'

      response.writeHead(200, {
        'Content-Disposition': `attachment; filename="${fileName}"`,
        'Content-Type': fileType,
      })
      response.end(zipFileContents)
    }
  })
})

demoRouter.post('/logs/:log_id/parse', (request, response) => {
  // parses the entire log file
  const data = {
    log_id: request.params.log_id,
  }

  const socket = request.app.get('socketio')
  socket.emit('QCAT_parse_all', data, (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
  })
})

demoRouter.post('/AT', (request, response) => {
  console.log(request.body)
  if (request.body.serial === undefined) {
    return response.status(400).send({ error : 'missing serial' })
  }
  const data = {
    id: generateShortId(8),
    serial: request.body.serial,
  }

  const socket = request.app.get('socketio')
  socket.emit('AT_start', data, (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
  })
})

demoRouter.delete('/AT/:id', (request, response) => {
  console.log(request.body)
  const socket = request.app.get('socketio')
  socket.emit('AT_stop', { id: request.params.id }, (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
  })
})

demoRouter.post('/AT/:id', (request, response) => {
  console.log(request.body)
  if (request.body.commands === undefined) {
    return response.status(400).send({ error : 'missing commands' })
  }
  const data = {
    id: request.params.id,
    commands: request.body.commands
  }

  const socket = request.app.get('socketio')
  socket.emit('AT_send', data, (res) => {
    if (res.error) {
      return response.status(400).send(res)
    }
    response.send(res)
  })
})

module.exports = demoRouter
