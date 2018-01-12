const ioHandlers = [];
let inPayload = '';

process.stdin.resume();
process.stdin.setEncoding('utf-8');
process.stdin.on('data', (data) => {
    if (data === '\n') {
        const currPayload = inPayload;
        ioHandlers.forEach(handler => setImmediate(() => handler(currPayload)));
        inPayload = '';
    } else {
        inPayload += data;
    }
});

const addIoHandler = handler => ioHandlers.push(handler);
const write = (outPayload) => {
    process.stdout.write(outPayload, 'utf-8');
    process.stdout.write('\n');
};

export default {
    addIoHandler,
    write,
};
