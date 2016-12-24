<template>
  <div class="stop" v-if="current_stop != null">
    <p class="title">Choisir ses trajets depuis {{ current_stop.name }}</p>
    <div v-for="(ls, i) in current_stop.line_stops">
      <label>
        <input type="checkbox" :name="ls.id" v-on:click="toggle_line_stop(ls)" :value="ls.id" v-model="line_stops"/>
        <strong>{{ ls.line.mode }} {{ ls.line.name }}</strong>
        vers {{ ls.direction.name }}
      </label>
    </div>
  </div>
  <div v-else>
    <p class="title">Choisir ses trajets ...</p>
    <div class="notification is-info">
      Veuillez sélectionner un arrêt pour ajouter un trajet.
    </div>
  </div>
</template>

<script>
module.exports = {
  props : {
    current_stop : Object,
    line_stops : Array,
  },
  methods : {
    toggle_line_stop : function(line_stop){
      // propagate
      this.$emit('toggle_line_stop', line_stop);
    },
  },
};
</script>
