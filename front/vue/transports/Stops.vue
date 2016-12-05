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

        // Unique sorted lines
        lines = _.sortBy(lines, function(l){
          return l.name;
        });
        lines = _.sortedUniqBy(lines, function(l){
          return l.id;
        });

        // Group by mode
        lines = _.groupBy(lines, function(l){
          return l.mode;
        });

        out[stop.id] = lines;
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
  <aside>
    <ul>
      <li v-on:click="selected(stop)" v-for="(stop, i) in stops" v-bind:class="{'is-active' : stop == current_stop}">
        <p class="name">
          <strong>{{ stop.name }}</strong> à 
          <em v-if="!stop.trip">{{ stop.approximate_distance }} m</em>
          <span v-if="stop.trip">{{ stop.trip.distance }} m - {{ stop.trip.duration|seconds }}</span>
        </p>
        <p class="lines">
          <p v-for="(mode_lines,mode) in lines[stop.id]">
            <span class="icon">
              <span class="fa fa-train" title="Tramway" v-if="mode == 'tram'"></span>
              <span class="fa fa-bus" title="Bus" v-if="mode == 'bus'"></span>
              <span class="fa fa-bus" title="Autocar" v-if="mode == 'car'"></span>
            </span>
            <span v-for="line in mode_lines" class="tag" :class="{'is-success' : line.mode == 'tram', 'is-primary' : line.mode == 'bus', 'is-info' : line.mode == 'car'}">{{ line.name }}</span>
          </p>
        </p>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
ul li {
  cursor: pointer;
  margin-bottom: 6px;
  border-radius: 3px 3px;
  padding: 3px;
}

ul li.is-active {
  background: #EEE;
}

ul li p {
  margin-bottom: 4px;
}

ul li p.name * {
  font-size: 1.2em !important;
}

ul li span.icon {
  color: #888;
}

ul li p span.tag {
  margin-right: 2px;
  margin-bottom: 2px;
}

</style>
