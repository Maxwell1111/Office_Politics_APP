/* eslint-disable @typescript-eslint/no-var-requires */
const { DefinePlugin } = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
/* eslint-enable @typescript-eslint/no-var-requires */

module.exports = {
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.(css)$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin(),
    new DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify('production')
      }
    }),
    new CompressionPlugin({
      filename: '[path][base].gz',
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 1024, // Only assets bigger than this size are processed. Adjust as needed.
      minRatio: 0.8 // Only if compression ratio is smaller than this.
    })
  ],
  devtool: 'source-map',
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin(
        {
          test: /\.js(\?.*)?$/i,
          parallel: 2,  // Reduced from true to limit memory usage
          extractComments: false,
          terserOptions: {
            compress: { drop_console: false },
            mangle: true,
            format: {
              comments: false
            }
          }
        }
      )
    ],
    // Split chunks to reduce memory during compilation
    splitChunks: {
      chunks: 'all',
      maxSize: 244000,  // Split large chunks
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10
        }
      }
    }
  }
};
