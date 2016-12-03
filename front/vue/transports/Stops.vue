<script>
var _ = require('lodash');

module.exports = {
  props : {
    'stops' : {
      type : Array,
      required : true,
    },
    'current_stop' : Object,
  },

  computed : {
    // List unique lines per stop
    // TODO: use some lodash magic here
    lines : function(){
      var out = {}
      this.stops.forEach(function(stop){
        var lines = []
        stop.line_stops.forEach(function(ls){
          lines.push(ls.line);
        });
        out[stop.id] = _.uniqBy(lines, function(l){
          return l.id;
        });
      });
      return out;
    },
  },

  filters : {
    seconds : function(s){
      var minutes = Math.round(s / 60);
      return minutes + ' minutes';
    },
  },
  methods : {
    selected : function(stop){
      this.$emit('selected_stop', stop);
    },
  },
}
</script>

<template>
  <aside class="menu">
    <ul class="menu-list">
      <li v-on:click="selected(stop)" v-for="(stop, i) in stops">
        <span class="name" v-bind:class="{'is-active' : stop == current_stop}">
          <strong>{{ stop.name }}</strong> à 
          <em v-if="!stop.trip">{{ stop.approximate_distance }} m</em>
          <span v-if="stop.trip">{{ stop.trip.distance }} m - {{ stop.trip.duration|seconds }}</span>
        </span>
        <ul>
<span v-for="line in lines[stop.id]" class="tag" :class="{'is-success' : line.mode == 'tram', 'is-primary' : line.mode == 'bus', 'is-info' : line.mode == 'car'}">{{ line.name }}</span>
        </ul>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
ul.menu-list li {
  cursor: pointer;
  margin-bottom: 6px;
}

ul.menu-list li ul {
  margin-top: 2px !important;
  margin-bottom: 2px !important;
}

ul.menu-list span.name {
  display: block;
  padding: 0 5px;
  border-radius: 3px 3px;
}

ul.menu-list span.is-active {
  background: #3273dc;
  color: white;
}

ul.menu-list span.is-active strong {
  color: white;
}

p.no-selection {
  font-size: 0.8em;
  margin-left: 8px;
  color: #CCC;
}
</style>
