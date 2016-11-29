<template>
  <form>
    <h1 class="title">Météo à {{ widget.city.name }}</h1>
    <div class="notification is-info">
      <span class="icon">
        <span class="fa fa-bolt"></span>
      </span>
      <span>
        Les prévisions météo s'afficheront ici.
      </span>
    </div>
    <p class="control">
      <span v-on:click="save(null)" class="button is-success" :class="{'is-loading' : saving}">
        <span class="icon">
          <i class="fa fa-bolt"></i>
        </span>
        <span>Mettre à jour</span>
      </span>
    </p>
  </form>
</template>

<script>
var mixins = require('./mixins.js');

module.exports = {
  mixins : [mixins, ],
};
</script>

