module.exports = {
  post: {
    tags: ['qConnect demo AT operations'],
    description: 'Connect to device serial port',
    operationId: 'connectAT',
    requestBody: {
      content: {
        'application/json': {
          schema: {
            $ref: '#/components/requestBodies/serial'
          },
        },
      },
    },
    responses: {
      200: {
        description: 'Connected to device serial port',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Session',
            },
          },
        },
      },
      400: {
        description: 'AT error',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Error',
            },
          },
        },
      },
    },
  },
}