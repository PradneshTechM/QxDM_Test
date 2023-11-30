const winston = require('winston')
require('winston-daily-rotate-file')

const { createLogger, format, transports } = winston
const { colorize, combine, printf } = format

const logger = createLogger({
  level: 'info',
  exitOnError: false,
  format: format.combine(
    format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    format.errors({ stack: true }),
    format.splat(),
    format.json(),
  ),
  defaultMeta: { service: 'qConnect-API' },
})

// https://github.com/winstonjs/winston/issues/1243
function devFormat() {
  const formatMessage = (info) => `${new Date().toLocaleString()} ${info.level} ${info.message}`
  const formatError = (info) => `${new Date().toISOString()} ${info.level} ${info.message}\n\n${info.stack}\n`
  const format = (info) => ((info instanceof Error) ? formatError(info) : formatMessage(info))
  return combine(colorize(), printf(format))
}

logger.add(new transports.Console({
  format: devFormat()
}))

module.exports = logger
