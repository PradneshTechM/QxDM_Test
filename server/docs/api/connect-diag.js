module.exports = {
  post: {
    tags: ['qConnect demo diag operations'],
    description: 'Connect to device diag port',
    operationId: 'connectDiag',
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
        description: 'Connected to device diag port',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/Session',
            },
          },
        },
      },
      400: {
        description: 'Diag error',
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