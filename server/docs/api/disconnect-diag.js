module.exports = {
  delete: {
    tags: ['qConnect demo diag operations'],
    description: 'Disconnect from device diag port',
    operationId: 'disconnectDiag',
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
        description: 'Disconnected from device diag port',
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