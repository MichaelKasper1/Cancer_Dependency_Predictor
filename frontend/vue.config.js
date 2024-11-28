const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  chainWebpack: config => {
    config.plugin('fork-ts-checker').tap(args => {
      args[0].typescript = {
        configFile: 'tsconfig.json'
      };
      return args;
    });
  }
})