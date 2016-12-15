<template>
  <form>
    <div class="notification is-info">
      <span class="icon">
        <span class="fa fa-bus"></span>
      </span>
      <span>
        Les perturbations concernant vos arrêts choisis s'afficheront ici.
      </span>
    </div>

    <p class="control">
      <select v-if="locations" class="select" v-model="selected_location">
        <option v-for="l in locations" :value="l.id">
          {{ l.name }} : {{ l.address }} à {{ l.city.name }}
        </option>
      </select>
    </p>

    <p class="control">
      <span v-on:click="save_location" class="button is-success" :class="{'is-loading' : saving}">
        <span class="icon">
          <i class="fa fa-check"></i>
        </span>
        <span>Enregistrer</span>
      </span>
      <span v-on:click="delete_widget" class="button is-danger" :class="{'is-loading' : deleting}">
        <span class="icon">
          <i class="fa fa-trash"></i>
        </span>
        <span>Supprimer</span>
      </span>
    </p>
    </p>
  </form>
</template>

<script>
var mixins = require('./mixins.js');

module.exports = {
  mixins : [mixins, ],
  data : function(){
    return {
      selected_location : null,
    };
  },
  computed : {
    locations : function(){
      return this.$store.state.locations;
    },
  },
  mounted : function(){
    // Select inital location
    this.$set(this, 'selected_location', this.widget.location);
  },
  methods: {
    save_location: function(){
      this.save({
        'location': this.selected_location,
      });
    },
  },
};
</script>
