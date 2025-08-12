const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'https://sentinelai-production.up.railway.app', // Railway production backend
      changeOrigin: true,
    })
  );
};
