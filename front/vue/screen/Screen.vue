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
  mounted : function(){
    var url = '/api/screen/' + this.slug + '/';
    this.$http.get(url).then(function(resp){
      this.$set(this, 'screen', resp.body);

      var store = this.$store;
      store.commit('use_screen', this.slug);
      this.screen.widgets.forEach(function(w){
        store.commit('add_widget', w);
      });
    });
  },
};
</script>

<template>
  <div class="tile is-ancestor" v-if="screen">
    <Group :group="group" :widgets="screen.widgets" v-for="group in screen.groups" />
  </div>
</template>
