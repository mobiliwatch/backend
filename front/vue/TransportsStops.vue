<template>
  <ul class="list-group">
    <li class="list-group-item" v-bind:class="{active : stop == current_stop}" v-on:click="selected(stop)" v-for="(stop, i) in stops">
      <span class="badge">{{ stop.distance }} m</span>
      {{ stop.name }}

      <ul>
        <li v-for="ls in line_stops_dict[stop.id]">
          {{ ls.line.mode }} {{ ls.line.name }} vers {{ ls.direction.name }}
        </li>
      </ul>
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
    'line_stops' : Array,
    'current_stop' : Object,
  },

  data : function(){
    return {
    }
  },

  computed : {
    // Order line stops per parent stop
    line_stops_dict : function(){
      var out = {};
      var selected_ls = this.line_stops;
      this.stops.forEach(function(s, i){
        out[s.id] = s.line_stops.filter(function(ls){
          return selected_ls.includes(ls.id);
        });
      });
      return out;
    },
  },

  methods : {
    selected : function(stop){
      this.$emit('selected_stop', stop);
    },
  },
}
</script>
