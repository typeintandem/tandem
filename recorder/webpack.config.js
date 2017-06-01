/* eslint-disable */
var path = require("path");
var HtmlWebpackPlugin = require('html-webpack-plugin');
module.exports = {
  entry: {
    main: './app/index.js',
    guest: './app/guest.js'
  },

  output: {
    path: __dirname + '/build',
    filename: 'bundle.[name].js'
  },

  module: {
    loaders: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      },
      {
        test: /\.(css|scss)/,
        loader: ['style-loader', 'css-loader', 'sass-loader'],
      }
    ],
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: __dirname + '/app/index.html',
      filename: 'index.html',
      inject: 'body'
    })
  ],

  resolve: {
    extensions: ['.js', '.jsx']
  },

  target: 'electron-main',
};
