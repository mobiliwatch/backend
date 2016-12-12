<script>
var Group = require('./Group.vue');

module.exports = {
  components : {
    Group : Group,
  },
  props : {
    slug : String,
  },
  data : function(){
    return {
      screen : null,
    };
  },  
  methods : {
    add_groups : function(groups){
      var that = this;
      groups.forEach(function(g){
        that.$store.commit('add_group', g);
        that.add_groups(g.groups); // recurse
      });
    },
  },
  mounted : function(){

    // Load screen details
    var url = '/api/screen/' + this.slug + '/';
    this.$http.get(url).then(function(resp){
      this.$set(this, 'screen', resp.body);

      var store = this.$store;
      store.commit('use_screen', this.slug);
      this.screen.widgets.forEach(function(w){
        store.commit('add_widget', w);
      });
      this.add_groups(this.screen.groups);
    });

    // Load locations
    var url = '/api/location/';
    this.$http.get(url).then(function(resp){
      this.$store.commit('use_locations', resp.body);
    });

    // Load cities
    var url = '/api/city/';
    this.$http.get(url).then(function(resp){
      this.$store.commit('use_cities', resp.body);
    });
  },
};
</script>

<template>
  <div class="tile is-ancestor" v-if="screen">
    <Group :groupId="group.id" v-for="group in screen.groups" />
  </div>
</template>
