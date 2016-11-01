// Js libs
var Vue = require('vue/dist/vue.js');
Vue.use(require('vue-resource'));
var Transports = require('vue/Transports.vue')

// Init generic Vue app
// with top components
var app = new Vue({
  el : '#app',
  components : {
    Transports : Transports,
  },
});

// Css
require('bootswatch-dist/css/bootstrap.css');
require('css/mobili.css');
