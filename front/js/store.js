var Vue = require('vue/dist/vue.js');
var Vuex = require('vuex');
var _ = require('lodash');

module.exports = new Vuex.Store({
  state: {
    widgets : {},
    groups : {},
    screen : '',
    locations : [],
    cities : [],
  },
  mutations: {
    use_screen : function(state, screen){
      state.screen = screen;
    },

    add_widget : function(state, widget){
      // Store an initial widget declaration in store
      state.widgets[widget.id] = widget;
    },

    use_locations : function(state, locations){
      state.locations = locations;
    },

    use_cities : function(state, cities){
      state.cities = cities;
    },

    add_group : function(state, group){
      // Store an initial group declaration in store
      state.groups[group.id] = group;
    },

    add_subgroup : function(state, payload){
      // Store an initial group declaration in store
      var parent_id = payload.parent;
      var child = payload.child;
      var groups = _.clone(state.groups);
      if(!groups[parent_id])
        throw new Error("No group "+parent_id);
      groups[parent_id]['groups'].push(child);
      groups[child.id] = child;
      Vue.set(state, 'groups', groups);
    },

    delete_group : function(state, payload){
      // Delete a group
      var groups = _.clone(state.groups);
      if(!groups[payload.id])
        throw new Error("No group "+parent_id);
      delete groups[payload.id];
      Vue.set(state, 'groups', groups);
    },

    update_group : function(state, payload){
      // Check input
			var group_id = payload.id;
      var group = state.groups[group_id];
      if(!group){
        console.warn('No group found for update', payload);
        return;
      }

			// Shallow Clone groups
			// Deep is not necessary here
			// This triggers global updates in components
			var groups = _.clone(state.groups);

      // Merge items from payload update
      var new_group = _.merge(group, payload);

			groups[group_id] = new_group;

      // Update groups in state
      Vue.set(state, 'groups', groups);
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

    delete_widget: function(state, payload){
      // Delete a widget
      var widgets = _.clone(state.widgets);
      if(!widgets[payload.id])
        throw new Error("No widget "+parent_id);
      delete widgets[payload.id];
      Vue.set(state, 'widgets', widgets);
    },

  },

  actions : {
    // Save widget update on backend, in a promise
    update_widget : function(context, payload){
			var widget_id = payload.id;
      var url = '/api/screen/' + context.state.screen + '/' + widget_id + '/';
      return Vue.http.patch(url, payload).then(function(){
          // Commit change on local store
          context.commit('update_widget', payload);
      });
    },

    // Save widget update on backend, in a promise
    add_subgroup : function(context, payload){
			var group_id = payload.id;
      var url = '/api/screen/' + context.state.screen + '/group/' + group_id + '/';

      return Vue.http.post(url).then(function(resp){
        // Add new group to local store
        context.commit('add_subgroup', {
          parent : group_id,
          child : resp.body,
        });
      });
    },

    // Delete a group on backend
    delete_group : function(context, payload){
			var group_id = payload.id;
      var url = '/api/screen/' + context.state.screen + '/group/' + group_id + '/';

      return Vue.http.delete(url).then(function(resp){
        // Add new group to local store
        context.commit('delete_group', {
          id : group_id,
        });
      });
    },

    // Save group update on backend, in a promise
    update_group : function(context, payload){
			var group_id = payload.id;
      var url = '/api/screen/' + context.state.screen + '/group/' + group_id + '/';
      return Vue.http.patch(url, payload).then(function(){
          // Commit change on local store
          context.commit('update_group', payload);
      });
    },

    // Add a new widget in a group
    add_widget : function(context, payload){
      var group_id = payload.group;
      var url = '/api/screen/' + context.state.screen + '/widgets/';
      return Vue.http.post(url, payload).then(function(resp){
          // Commit change on local store
          context.commit('add_widget', resp.body);

          // Update group to use this widget
          var widgets = context.state.groups[group_id].widgets;
          widgets.push(resp.body.id);
          context.commit('update_group', {
            id : payload.group_id,
            widgets : widgets,
          });
      });
    },

    // Delete a widget on backend
    delete_widget : function(context, payload){
			var widget_id = payload.id;
      var url = '/api/screen/' + context.state.screen + '/' + widget_id + '/';

      return Vue.http.delete(url).then(function(){
        context.commit('delete_widget', {
          id : widget_id,
        });
      });
    },
  }
});
