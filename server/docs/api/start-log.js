module.exports = {
  post: {
    tags: ['qConnect demo log operations'],
    description: 'Start logging from connected device diag',
    operationId: 'startLog',
    requestBody: {
      content: {
        'application/json': {
          schema: {
            $ref: '#/components/requestBodies/id'
          },
        },
      },
    },
    responses: {
      200: {
        description: 'Started logging from device diag port',
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