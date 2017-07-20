const path = require('path');

module.exports = () => ({
  entry: {
    main: path.resolve(__dirname, '../../app/index.js'),
  },

  output: {
    path: path.resolve(__dirname, '../../../build/main'),
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

  plugins: [],

  resolve: {
    alias: {
      components: path.resolve(__dirname, '../../app/components'),
      models: path.resolve(__dirname, '../../app/models'),
      pages: path.resolve(__dirname, '../../app/pages'),
      'recorder-app': './recorder/DownloadApp',
    },
    extensions: ['.js', '.jsx'],
  },
});
