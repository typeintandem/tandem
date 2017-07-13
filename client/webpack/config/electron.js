const path = require('path');
const config = require('./base.js')();

config.entry.guest = path.resolve(__dirname, '../../app/guest.js');
config.output.path = path.resolve(__dirname, '../../build/electron');
config.resolve.alias['recorder-app'] = './recorder/RecorderApp';
config.target = 'electron-main';

module.exports = config;
