module.exports = {
  get: {
    tags: ['qConnect demo log operations'],
    description: 'Get a processed log',
    operationId: 'getLog',
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
        description: 'Fetched log',
        content: {
          'text/csv': {
            schema: {
              type: 'string',
              format: 'binary',
            },
          },
        },
      },
      400: {
        description: 'Log fetching error',
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