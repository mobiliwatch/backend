var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require("extract-text-webpack-plugin");


module.exports = {
  context: __dirname,

  entry: './front/js/index',

  output: {
      path: path.resolve('./front/bundles/'),
      filename: "[name]-[hash].js",
  },

  plugins: [
    new BundleTracker({filename: './front/webpack-stats.json'}),
    new ExtractTextPlugin("style-[hash].css", {allChunks: false})
  ],

  module: {
    loaders: [
      {
        // Load css directly
        test: /\.css$/,
        loader: ExtractTextPlugin.extract("style-loader", "css-loader")
      },
      {
        // Support images
        test: /\.(png|jpg|jpeg)$/,
        loader: 'file?name=images/[name].[ext]'
      },
      {
        // Support fonts
        test: /\.(eot|svg|ttf|woff|woff2)/,
        loader: 'file?name=fonts/[name].[ext]'
      },
      {
        // Vue components
        test: /\.vue$/,
        loader: 'vue'
      },
    ]
  },

  resolve: {
    modulesDirectories: ['node_modules', 'bower_components', 'front', ],
    extensions: ['', '.js', '.vue', '.css']
  },
}
