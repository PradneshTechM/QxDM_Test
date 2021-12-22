module.exports = {
  delete: {
    tags: ['qConnect demo AT operations'],
    description: 'Disconnect from device serial port',
    operationId: 'disconnectAT',
    parameters: [
      {
        name: 'id',
        in: 'path',
        schema: {
          $ref: '#/components/parameters/id',
        },
        required: true,
        description: 'A session id',
      },
    ],
    responses: {
      200: {
        description: 'Disconnected from device serial port',
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