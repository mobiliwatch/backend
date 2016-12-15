<template>
  <form>
    <div class="notification is-danger" v-if="error">
      <span class="icon">
        <span class="fa fa-exclamation-triangle"></span>
      </span>
      <span v-if="error.body && error.body.detail">
        {{ error.body.detail }}
      </span>
    </div>
    <div class="notification is-info" v-else>
      <span class="icon">
        <span class="fa fa-bolt"></span>
      </span>
      <span>
        Les prévisions météo s'afficheront ici.
      </span>
    </div>

    <p class="control">
      <select v-if="cities && selected_city" class="select" v-model="selected_city">
        <option v-for="city in cities" :value="city.id">
          {{ city.name }}
        </option>
      </select>
    </p>

    <p class="control">
      <span v-on:click="save_city" class="button is-success" :class="{'is-loading' : saving}">
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
      selected_city : null,
    };
  },
  computed : {
    cities : function(){
      return this.$store.state.cities;
    },
  },
  mounted : function(){
    // Select inital city
    this.$set(this, 'selected_city', this.widget.city);
  },
  methods: {
    save_city: function(){
      this.save({
        'city': this.selected_city,
      });
    },
  },
};
</script>
