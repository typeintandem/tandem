'use babel';

import path from 'path';
import childProcess from 'child_process';

const spawnAgent = (args) => {
  const dirname = path.resolve(__dirname);
  const filename = path.join(dirname, '../agent/main.py');

  const fileArgs = args || [];
  fileArgs.unshift(filename);

  return childProcess.spawn('python3', fileArgs);
};

const random = (lo, hi) => {
  const min = Math.ceil(lo);
  const max = Math.floor(hi);

  return Math.floor((Math.random() * (max - min)) + min);
};

const getStringPort = () =>
  String(random(60600, 62600));

const createPatches = event =>
  [
    {
      start: {
        row: event.oldRange.start.row,
        column: event.oldRange.start.column,
      },
      end: {
        row: event.oldRange.end.row,
        column: event.oldRange.end.column,
      },
      text: '',
    },
    {
      start: {
        row: event.oldRange.start.row,
        column: event.oldRange.start.column,
      },
      end: {
        row: 0,
        column: 0,
      },
      text: event.newText,
    },
  ];

const eventForBuffer = buffer => (
  {
    oldRange: {
      start: {
        row: 0,
        column: 0,
      },
      end: {
        row: 0,
        column: 0,
      },
    },
    newText: buffer.getText(),
  }
);


export default {
  createPatches,
  eventForBuffer,
  spawnAgent,
  getStringPort,
};
