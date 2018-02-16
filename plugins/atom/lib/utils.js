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

export default {
  spawnAgent,
  getStringPort,
};
