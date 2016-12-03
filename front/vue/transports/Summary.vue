<script>
var _ = require('lodash');

module.exports = {
  props : {
    line_stops : Array,
    stops : {
      type : Array,
      required : true,
    },
  },

  computed : {
    // Order line stops per parent stop
    line_stops_list : function(){
      var out = [];
      var selected_ls = this.line_stops;
      this.stops.forEach(function(s, i){
        out = _.concat(out, s.line_stops.filter(function(ls){
          return selected_ls.includes(ls.id);
        }));
      });
      return out;
    },
  },

}
</script>

<template>
  <div>
    <h1 class="title">Summary</h1>

    <ul v-if="line_stops_list.length">
      <li v-for="ls in line_stops_list">
        {{ ls.line.mode }} {{ ls.line.name }} vers {{ ls.direction.name }}
      </li>
    </ul>
    <p class="no-selection" v-else>
      <span class="icon is-small">
        <span class="fa fa-bus"></span>
      </span>
      Aucune ligne sélectionée pour cet arrêt.
    </p>

  </div>
</template>
