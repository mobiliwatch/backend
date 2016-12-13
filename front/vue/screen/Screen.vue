<script>
var Group = require('./Group.vue');
var Toggle = require('../ToggleButton.vue');

module.exports = {
  components : {
    Group : Group,
    Toggle : Toggle,
  },
  props : {
    slug : String,
  },
  data : function(){
    return {
    };
  },  
  computed : {
    screen : function(){
      return this.$store.state.screen;
    },
  },
  methods : {
    update_screen : function(){
      // Trigger a full screen update
      this.$store.dispatch('update_screen', {
        style : this.screen.style,
      });
    },
  },
  mounted : function(){

    // Load screen details
    var url = '/api/screen/' + this.slug + '/';
    this.$http.get(url).then(function(resp){
      this.$store.commit('use_screen', resp.body);
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
  <div class="editor" v-if="screen">
    <div class="actions">
      <Toggle option1="light" option2="dark" v-model="screen.style" v-on:input="update_screen"/>
    </div>
    <div class="tile is-ancestor">
      <Group :groupId="group.id" v-for="group in screen.groups" />
    </div>
  </div>
</template>
