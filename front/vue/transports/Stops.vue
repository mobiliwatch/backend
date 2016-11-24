<template>
  <aside class="menu">
    <ul class="menu-list">
      <li v-on:click="selected(stop)" v-for="(stop, i) in stops">
        <a href="javascript:null" v-bind:class="{'is-active' : stop == current_stop}">
          <strong>{{ stop.name }}</strong> à {{ stop.distance }} m
        </a>

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

ul.menu-list a {
  padding-bottom: 0 !important;
  padding-top: 1px !important;
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
