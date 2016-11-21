<script>
var Group = require('./WidgetGroup.vue');

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
    });
  },
};
</script>

<template>
  <div class="tile is-ancestor" v-if="screen">
    <Group :group="group" :widgets="screen.widgets" v-for="group in screen.groups" />
  </div>
</template>
