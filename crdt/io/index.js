const ioHandlers = [];
let inPayload = '';

process.stdin.resume();
process.stdin.setEncoding('ascii');
process.stdin.on('data', (data) => { inPayload += data; });
process.stdin.on('end', () => {
    ioHandlers.forEach(handler => handler(inPayload));
    inPayload = '';
});

const addIoHandler = handler => ioHandlers.push(handler);
const write = (outPayload) => {
    process.stdout.write(outPayload);
    process.stdout.write('\n');
};

export default {
    addIoHandler,
    write,
};
