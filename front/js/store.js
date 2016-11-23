var Vue = require('vue');
var Vuex = require('vuex');

module.exports = new Vuex.Store({
  state: {
    widgets : {},
  },
  mutations: {
    add_widget : function(state, widget){
      // Store an initial widget declaration in store
      state.widgets[widget.id] = widget;
    },
  }
})

