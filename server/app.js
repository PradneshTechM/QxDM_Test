const express = require('express')
const middleware = require('./utils/middleware')
const app = express()
const swaggerUI = require('swagger-ui-express')
const docs = require('./docs')

app.use(express.json())
app.use(middleware.requestLogger)

// need cors?
app.use('/api', require('./controllers/demo'))
app.use('/api-docs', swaggerUI.serve, swaggerUI.setup(docs))

app.use(middleware.unknownEndpoint)

module.exports = app
