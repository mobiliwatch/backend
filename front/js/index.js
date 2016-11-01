// Js libs
var Vue = require('vue/dist/vue.js');
Vue.use(require('vue-resource'));
var Transports = require('vue/Transports.vue')

var app = new Vue({
  el : '#app',
  components : {
    Transports : Transports,
  },

});

// Css
require('bootswatch-dist/css/bootstrap.css');
require('leaflet/dist/leaflet.css');
require('Leaflet.extra-markers/dist/css/leaflet.extra-markers.min.css');
require('css/mobili.css');
