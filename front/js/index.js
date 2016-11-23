// Js libs
var Vue = require('vue/dist/vue.js');
Vue.use(require('vue-resource'));
Vue.use(require('vuex'));
var Transports = require('vue/Transports.vue')
var Screen = require('vue/Screen.vue')

// Add csrf token
Vue.http.headers.common['X-CSRFTOKEN'] = document.querySelector('#csrf').getAttribute('content');

// Use vuex store
var store = require('./store.js');

// Init generic Vue app
// with top components
var app = new Vue({
  store : store,
  el : '#app',
  components : {
    Transports : Transports,
    Screen : Screen,
  },
});

// Css
require('bulma/css/bulma.css');
require('font-awesome/css/font-awesome.css');
require('css/mobili.css');
