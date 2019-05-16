const winston = require('winston')
require('winston-daily-rotate-file')
const { createLogger, format, transports } = winston
const { colorize, combine, printf } = format

//  Write all logs error (and below) to `error.log`.
const transportError = new (winston.transports.DailyRotateFile)({
  dirname: 'logs',
  filename: '%DATE%_error.log', 
  maxSize: '20m',
  maxFiles: '14d',
  level: 'error' 
})

// Write to all logs with level `info` and below to `combined.log`
const transportAll = new (winston.transports.DailyRotateFile)({
  dirname: 'logs',
  filename: '%DATE%_combined.log', 
  maxSize: '20m',
  maxFiles: '14d'
})

const logger = createLogger({
  level: 'info',
  exitOnError: false,
  format: format.combine(
    format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    format.errors({ stack: true }),
    format.splat(),
    format.json()
  ),
  defaultMeta: { service: 'appium-manager' },
  transports: [
    transportError,
    transportAll
  ]
})

// https://github.com/winstonjs/winston/issues/1243
function devFormat() {
  const formatMessage = info => `${new Date().toLocaleString()} ${info.level} ${info.message}`;
  const formatError = info => `${new Date().toISOString()} ${info.level} ${info.message}\n\n${info.stack}\n`;
  const format = info => info instanceof Error ? formatError(info) : formatMessage(info);
  return combine(colorize(), printf(format))
}

// If we're not in production then **ALSO** log to the `console`
// with the colorized simple format.
if (process.env.NODE_ENV !== 'production') {
  logger.add(new transports.Console({ 
    format: devFormat()
  }))
}

module.exports = logger;
