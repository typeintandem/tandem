const path = require('path');
const config = require('./base.js')();
const HtmlWebpackPlugin = require('html-webpack-plugin');

config.entry.guest = path.resolve(__dirname, '../../app/guest.js');
config.output.path = path.resolve(__dirname, '../../../build/electron');
config.resolve.alias['recorder-app'] = './recorder/RecorderApp';
config.plugins.push(
  new HtmlWebpackPlugin({
    template: path.resolve(__dirname, '../../app/index.html'),
    filename: 'index.html',
    inject: 'body',
  }),
);
config.target = 'electron-main';

module.exports = config;
