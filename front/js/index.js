// Js libs
var Vue = require('vue/dist/vue.js');
Vue.use(require('vue-resource'));
var Transports = require('vue/Transports.vue')

// Add csrf token
Vue.http.headers.common['X-CSRFTOKEN'] = document.querySelector('#csrf').getAttribute('content');

// Init generic Vue app
// with top components
var app = new Vue({
  el : '#app',
  components : {
    Transports : Transports,
  },
});

// Css
require('bulma/css/bulma.css');
require('font-awesome/css/font-awesome.css');
require('css/mobili.css');
