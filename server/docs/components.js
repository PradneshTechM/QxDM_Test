module.exports = {
  components: {
    parameters: {
      id: {
        type: 'string',
        description: 'An id of a session',
        example: '665f9d3de25c474e',
      },
      log_id: {
        type: 'string',
        description: 'An id of a log',
        example: '665f9d3d',
      },
    },
    requestBodies: {
      serial: {
        type: 'object',
        properties: {
          serial: {
            type: 'string',
            description: 'The adb serial number of device',
            example: '94KBA0090A',
          },
        },
      },
      id: {
        type: 'object',
        properties: {
          id: {
            type: 'string',
            description: 'An id of a session',
            example: '665f9d3de25c474e',
          },
        },
      },
      test_case: {
        type: 'object',
        properties: {
          test_case: {
            type: 'string',
            description: 'the test case',
            example: 'TC1',
          },
        },
      },
      AT_Command: {
        type: 'string',
        description: 'An AT command',
        example: 'ATI',
      },
    },
    schemas: {
      // Session model
      Session: {
        type: 'object',
        properties: {
          data: {
            type: 'object',
            properties: {
              id: {
                type: 'string',
                description: 'id of the session',
                example: 'cc3c97049f16b61e',
              },
              status: {
                type: 'string',
                description: 'status message',
                example: 'connected diag',
              },
            },
          },
        },
      },
      // Log session model
      LogSession: {
        type: 'object',
        properties: {
          data: {
            type: 'object',
            properties: {
              id: {
                type: 'string',
                description: 'id of the session',
                example: 'cc3c97049f16b61e',
              },
              log_id: {
                type: 'string',
                description: 'id of the logging session',
                example: '665f9d3d',
              },
              status: {
                type: 'string',
                description: 'status message',
                example: 'started logging',
              },
            },
          },
        },
      },
      // AT response model
      AT_Response: {
        type: 'object',
        properties: {
          command: {
            type: 'string',
            description: 'An AT command',
            example: 'AT',
          },
          response: {
            type: 'string',
            description: 'Response from an AT command sent to device',
            example: 'OK',
          },
        },
      },
      // error model
      Error: {
        type: 'object',
        properties: {
          error: {
            type: 'string',
            description: 'Error message',
            example: 'missing test_case',
          },
        },
      },
    },
  },
}