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
      // Are we using the full editor ?
      advanced_editor : false,
    };
  },  
  computed : {
    screen : function(){
      return this.$store.state.screen;
    },
    editor : function(){
      return this.$store.state.editor;
    },
  },
  methods : {
    update_screen : function(){
      // Trigger a full screen update
      this.$store.dispatch('update_screen', {
        style : this.screen.style,
      });
    },
    switch_editor : function(editor){
      this.$store.commit('use_editor', editor);
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
  <div>
    <div class="editor" v-if="screen" :class="editor">
      <nav class="level">
        <div class="level-left">
          <span class="button" v-on:click="switch_editor('advanced')" v-if="editor != 'advanced'">
            <span class="icon is-small">
              <span class="fa fa-cogs"></span>
            </span>
            <span>Éditeur avancé</span>
          </span>
          <span class="button" v-on:click="switch_editor('normal')" v-if="editor != 'normal'">
            <span class="icon is-small">
              <span class="fa fa-pencil"></span>
            </span>
            <span>Éditeur standard</span>
          </span>
          <a :href="screen.frontend_url" target="_blank" class="button is-primary">
            <span class="icon is-small">
              <span class="fa fa-desktop"></span>
            </span>
            <span>Voir l'écran</span>
          </a>
        </div>
        <div class="level-right">
          <span class="level-item">
            <Toggle option1="light" option2="dark" v-model="screen.style" v-on:input="update_screen"/>
          </span>
        </div>
      </nav>
      <div class="notification is-warning" v-if="editor == 'advanced'">
        <span class="icon">
          <span class="fa fa-warning"></span>
        </span>
        <span>L'éditeur avancé est une fonctionalité en beta, la qualité de l'affichage peut laisser à désirer...</span>
      </div>
      <hr />
      <div class="tile is-ancestor">
        <Group :groupId="group.id" v-for="group in screen.groups" />
      </div>
    </div>
    <div class="notification is-info" v-else>
      Chargement de l'écran...
    </div>
  </div>
</template>
