module.exports = {
  delete: {
    tags: ['qConnect demo log operations'],
    description: 'Stop logging from connected device diag',
    operationId: 'stopLog',
    parameters: [
      {
        name: 'log_id',
        in: 'path',
        schema: {
          $ref: '#/components/parameters/log_id',
        },
        required: true,
        description: 'A log session id',
      },
    ],
    responses: {
      200: {
        description: 'Stopped logging from device diag port',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/LogSession',
            },
          },
        },
      },
      400: {
        description: 'Logging error',
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