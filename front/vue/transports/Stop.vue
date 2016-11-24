<template>
  <div class="stop">
    <div class="well" v-if="current_stop != null">
      <h5>{{ current_stop.name }}</h5>
      <div v-for="(ls, i) in current_stop.line_stops">
        <label>
          <input type="checkbox" :name="ls.id" v-on:click="toggle_line_stop(ls)" :value="ls.id" v-model="line_stops"/>
          <strong>{{ ls.line.mode }} {{ ls.line.name }}</strong>
          vers {{ ls.direction.name }}
        </label>
      </div>
    </div>

    <div class="notification is-info" v-if="current_stop == null">
      Veuillez sélectionner un arrêt pour voir les détails.
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
