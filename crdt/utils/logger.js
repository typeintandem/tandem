import winston from 'winston';

const prefix = Date.now();
const format = winston.format.printf(info => `[${info.timestamp}] [${info.level}]: ${info.message}`);

export default winston.createLogger({
    format: winston.format.combine(winston.format.label(), winston.format.timestamp(), format),
    transports: [
        new winston.transports.File({ filename: `/tmp/tandem-crdt-${prefix}.log` }),
        new winston.transports.File({ filename: `/tmp/tandem-crdt-debug-${prefix}.log`, level: 'debug' }),
    ],
});
