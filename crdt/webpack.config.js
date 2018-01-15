const path = require('path');

module.exports = {
    entry: [
        './index.js'
    ],

    target: 'node',

    output: {
        path: path.resolve(__dirname, 'build'),
        filename: 'bundle.js'
    },

    module: {
        loaders: [
            { test: /\.js$/, exclude: /node_modules/, loader: 'babel-loader'},
        ]
    }
};
