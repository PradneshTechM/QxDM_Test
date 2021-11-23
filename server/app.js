const express = require('express')

const app = express()

// need cors?
app.use('/api', require('./controllers/demo'))

const unknownEndpoint = (req, res) => {
  res.status(404).send({ error: 'unknown endpoint' })
}

app.use(unknownEndpoint)

module.exports = app
