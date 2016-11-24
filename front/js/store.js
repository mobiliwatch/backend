var Vue = require('vue/dist/vue.js');
var Vuex = require('vuex');
var _ = require('lodash');

module.exports = new Vuex.Store({
  state: {
    widgets : {},
    screen : '',
  },
  mutations: {
    use_screen : function(state, screen){
      state.screen = screen;
    },
    add_widget : function(state, widget){
      // Store an initial widget declaration in store
      state.widgets[widget.id] = widget;
    },
    update_widget : function(state, payload){
      // Check input
			var widget_id = payload.id;
      var widget = state.widgets[widget_id];
      if(!widget){
        console.warn('No widget found for update', payload);
        return;
      }

			// Shallow Clone widgets
			// Deep is not necessary here
			// This triggers global updates in components
			var widgets = _.clone(state.widgets);

      // Merge items from payload update
      var new_widget = _.merge(widget, payload);

			widgets[widget_id] = new_widget;

      // Update widgets in state
      Vue.set(state, 'widgets', widgets);
      console.debug('Updated widget', widget_id, payload);
    },
  },

  actions : {
    update_widget : function(context, payload){
      // Save widget update on backen, in a promise
			var widget_id = payload.id;
      var url = '/api/screen/' + context.state.screen + '/' + widget_id + '/';
      return Vue.http.patch(url, payload).then(function(){
          // Commit change on local store
          context.commit('update_widget', payload);
      });
      return new Promise(function(resolve, reject){


        setTimeout(function(){



          resolve();
        }, 1000)
      });
    },
  }
})

