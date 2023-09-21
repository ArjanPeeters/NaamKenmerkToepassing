import * as path from 'path';
import * as webpack from 'webpack';
import * as MiniCssExtractPlugin from 'mini-css-extract-plugin';
import { TsconfigPathsPlugin } from 'tsconfig-paths-webpack-plugin';

const config: webpack.Configuration = {
    entry: './src/ts/index.ts',
    mode: 'production',
    devtool: 'inline-source-map',
    target: ['web', 'es5'],
    output: {
        filename: 'scripts.js',
        path: path.resolve(__dirname, 'static'),
    },
    performance: {
        maxAssetSize: 1024 * 1024 * 5,
        maxEntrypointSize: 1024 * 1024 * 2,
    },
    module: {
        rules: [

            /**
             * TypeScript files
             */
            {
                test: /\.tsx?$/,
                exclude: /node_modules/,
                use: 'ts-loader',
            },

            /**
             * Stylesheet files
             */
            {
                test: /\.scss$/i,
                exclude: /node_modules/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: 'css-loader',
                        options: { url: false },
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: { autoprefixer: {} },
                            },
                        },
                    },
                    'sass-loader',
                ],
            },
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
        plugins: [new TsconfigPathsPlugin()],
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'style.css',
        }),
    ],
};

export default config;
