'use strict';
const path = require('path');
const webpack = require('webpack');
// const HtmlWebpackPlugin = require('html-webpack-plugin');
// const CopyWebpackPlugin = require('copy-webpack-plugin');
const ExtractTextPlugin = require('extract-text-webpack-plugin')

const _ = {};
_.cwd = (file) => {
  return path.join(process.cwd(), file || '')
}

_.cssLoader = 'css-loader?-autoprefixer'

_.cssProcessors = [
  {loader: '', test: /\.css$/},
  {loader: 'sass-loader?sourceMap', test: /\.scss$/},
  {loader: 'less-loader?sourceMap', test: /\.less$/},
  {loader: 'stylus-loader?sourceMap', test: /\.styl$/},
  {loader: 'sass-loader?indentedSyntax&sourceMap', test: /\.sass$/},
]

_.outputPath = path.join(__dirname, 'static')


// https://github.com/egoist/vbuild/blob/master/lib/vue-loaders.js
_.loadersOptions = () => {
  const isProd = process.env.NODE_ENV === 'production'

  function generateLoader(langs) {
    langs.unshift('css-loader?sourceMap&-autoprefixer')
    if (!isProd) {
      return ['vue-style-loader'].concat(langs).join('!')
    }
    return ExtractTextPlugin.extract({
      fallback: 'vue-style-loader',
      use: langs.join('!')
    })
  }

  return {
    minimize: isProd,
    options: {
      // css-loader relies on context
      context: process.cwd(),
      vue: {
        loaders: {
          css: generateLoader([]),
          sass: generateLoader(['sass-loader?indentedSyntax&sourceMap']),
          scss: generateLoader(['sass-loader?sourceMap']),
          less: generateLoader(['less-loader?sourceMap']),
          stylus: generateLoader(['stylus-loader?sourceMap']),
          js: 'babel-loader'
        }
      }
    }
  }
}

module.exports = {
  entry: {
    client: './js/main.js'
  },
  output: {
    path: path.resolve('./static'),
    filename: '[name].js',
    publicPath: path.resolve('./static'),
    // Point sourcemap entries to original disk location
    devtoolModuleFilenameTemplate: info => path.resolve(info.absoluteResourcePath),
    // Add /* filename */ comments to generated require()s in the output.
    pathinfo: true
  },
  performance: {
    hints: process.env.NODE_ENV === 'production' ? 'warning' : false
  },
  resolve: {
    extensions: ['.js', '.vue', '.css', '.json'],
    alias: {
      root: path.join(__dirname, '../client'),
      components: path.join(__dirname, '../client/components')
    },
    modules: [
      path.resolve('node_modules'),
      // this meanse you can get rid of dot hell
      // for example import 'components/Foo' instead of import '../../components/Foo'
      path.resolve('js')
    ]
  },
  module: {
    loaders: [
      {
        test: /\.vue$/,
        loaders: ['vue-loader']
      },
      {
        test: /\.js$/,
        loaders: ['babel-loader'],
        exclude: [/node_modules/]
      },
      {
        test: /\.es6$/,
        loaders: ['babel-loader']
      },
      {
        test: /\.(ico|jpg|png|gif|eot|otf|webp|ttf|woff|woff2)(\?.*)?$/,
        loader: 'file-loader',
        query: {
          name: 'static/media/[name].[hash:8].[ext]'
        }
      },
      {
        test: /\.svg$/,
        loader: 'raw-loader'
      }
    ]
  },
  plugins: [
    new webpack.LoaderOptionsPlugin(_.loadersOptions()),
  ],
  target: 'web'
};