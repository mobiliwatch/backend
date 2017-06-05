// Js libs
var Vue = require('vue/dist/vue.js');
Vue.use(require('vue-resource'));
Vue.use(require('vuex'));
var Transports = require('vue/transports/Transports.vue')
var Screen = require('vue/screen/Screen.vue')
var Trip = require('vue/trip/Trip.vue')

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
    Trip : Trip,
  },
});

// Css
require('bulma/bulma.sass');
require('font-awesome/scss/font-awesome.scss');
require("../style/main.scss");
