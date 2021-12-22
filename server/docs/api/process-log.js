module.exports = {
  post: {
    tags: ['qConnect demo log operations'],
    description: 'Process a saved log',
    operationId: 'processLog',
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
    requestBody: {
      content: {
        'application/json': {
          schema: {
            $ref: '#/components/requestBodies/test_case'
          },
        },
      },
    },
    responses: {
      200: {
        description: 'Log processed',
        content: {
          'application/json': {
            schema: {
              $ref: '#/components/schemas/LogSession',
            },
          },
        },
      },
      400: {
        description: 'Log processing error',
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