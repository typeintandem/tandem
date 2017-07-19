const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = () => ({
  entry: {
    main: path.resolve(__dirname, '../../app/index.js'),
  },

  output: {
    path: path.resolve(__dirname, '../../build/main'),
    filename: 'bundle.[name].js',
  },

  module: {
    loaders: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
      },
      {
        test: /\.(css|scss)/,
        loader: ['style-loader', 'css-loader', 'sass-loader'],
      },
    ],
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, '../../app/index.html'),
      filename: 'index.html',
      inject: 'body',
    }),
  ],

  resolve: {
    alias: {
      components: path.resolve(__dirname, '../../app/components'),
      pages: path.resolve(__dirname, '../../app/pages'),
      'recorder-app': './recorder/DownloadApp',
    },
    extensions: ['.js', '.jsx'],
  },
});
