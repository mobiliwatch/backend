var config = require('./webpack.config'),
    webpack = require('webpack'),
    path = require("path");
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var WebpackCleanupPlugin = require('webpack-cleanup-plugin');

// Output generated files in dist
config.output = {
  path: path.resolve('./front/dist/'),
  filename: "mobili-[hash].js",
};

// Output stats in dist
config.plugins = [
  new BundleTracker({
    filename: './front/dist/webpack-stats.json',
  }),
  new ExtractTextPlugin("mobili-[hash].css", {allChunks: false}),
  new WebpackCleanupPlugin({
    exclude : ['webpack-stats.json', ],
  }),
];

// Minimize js
config.plugins.push(new webpack.optimize.UglifyJsPlugin({minimize: true}));

module.exports = config;
