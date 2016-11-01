<template>
  <ul class="list-group">
    <li class="list-group-item" v-bind:class="{active : stop == current_stop}" v-on:click="selected(stop)" v-for="(stop, i) in stops">
      {{ stop.name }}
    </li>
  </ul>
</template>

<style scoped>
ul li.list-group-item {
  cursor: pointer;
}
</style>

<script>
module.exports = {
  props : {
    'stops' : {
      type : Array,
      required : true,
    },
    'current_stop' : Object,
  },

  data : function(){
    return {
    }
  },

  methods : {
    selected : function(stop){
      this.$emit('selected_stop', stop);
    },
  },
}
</script>
