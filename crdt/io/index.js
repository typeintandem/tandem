const ioHandlers = [];
let currentPayload = '';

process.stdin.resume();
process.stdin.setEncoding('utf-8');
process.stdin.on('data', (data) => {
    const payloadList = (currentPayload + data).split('\n');
    currentPayload = payloadList.pop();
    payloadList.forEach((payload) => {
        ioHandlers.forEach(handler => setImmediate(() => handler(payload)));
    });
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
