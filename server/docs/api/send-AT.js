module.exports = {
  post: {
    tags: ['qConnect demo AT operations'],
    description: 'Get response from AT command(s)',
    operationId: 'sendAT',
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
    requestBody: {
      content: {
        'application/json': {
          schema: {
            type: 'object',
            properties: {
              commands: {
                type: 'array',
                items: {
                  $ref: '#/components/requestBodies/AT_Command',
                },
              },
            },
          },
        },
      },
    },
    responses: {
      200: {
        description: 'Fetched AT response(s)',
        content: {
          'application/json': {
            schema: {
              type: 'array',
              items: {
                $ref: '#/components/schemas/AT_Response',
              }
            },
          },
        },
      },
      400: {
        description: 'AT response(s) fetching error',
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