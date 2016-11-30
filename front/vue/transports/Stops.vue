<template>
  <aside class="menu">
    <ul class="menu-list">
      <li v-on:click="selected(stop)" v-for="(stop, i) in stops">
        <span class="name" v-bind:class="{'is-active' : stop == current_stop}">
          <strong>{{ stop.name }}</strong> à 
          <em v-if="!stop.trip">{{ stop.approximate_distance }} m</em>
          <span v-if="stop.trip">{{ stop.trip.distance }} m - {{ stop.trip.duration|seconds }}</span>
        </span>

        <ul v-if="line_stops_dict[stop.id].length">
          <li v-for="ls in line_stops_dict[stop.id]">
            {{ ls.line.mode }} {{ ls.line.name }} vers {{ ls.direction.name }}
          </li>
        </ul>
        <p class="no-selection" v-else>
          <span class="icon is-small">
            <span class="fa fa-bus"></span>
          </span>
          Aucune ligne sélectionée pour cet arrêt.
        </p>

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

  filters : {
    seconds : function(s){
      var minutes = Math.round(s / 60);
      return minutes + ' minutes';
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
