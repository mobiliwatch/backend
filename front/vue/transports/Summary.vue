<script>
var _ = require('lodash');

module.exports = {
  props : {
    screens : Array,
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
  <div class="columns">
    <div class="column is-two-thirds">
      <ul v-if="line_stops_list.length">
        <li v-for="ls in line_stops_list">
          {{ ls.stop.name }} : 
          {{ ls.line.mode }} {{ ls.line.name }} vers {{ ls.direction.name }}
        </li>
      </ul>
      <p class="no-selection" v-else>
        <span class="icon is-small">
          <span class="fa fa-bus"></span>
        </span>
        Aucune ligne sélectionée.
      </p>
    </div>

    <div class="column is-one-third">
      <a :href="'/screen/' + screen.slug" class="button is-outlined is-success" v-for="screen in screens">
        <span class="icon is-small">
          <span class="fa fa-desktop"></span>
        </span>
        <span>{{ screen.name }}</span>
      </a>
      <a href="/screen/new/" class="button is-outlined is-info">
        <span class="icon is-small">
          <span class="fa fa-plus"></span>
        </span>
        <span>Ajouter un écran</span>
      </a>
    </div>
  </div>
</template>
