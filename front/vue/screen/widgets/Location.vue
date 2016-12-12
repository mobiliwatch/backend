<template>
  <form>

    <h1 class="title">Prochains passages</h1>
    <div class="notification is-info">
      <span class="icon">
        <span class="fa fa-bus"></span>
      </span>
      <span>
        Les horaires des prochains passages de vos arrêts choisis s'afficheront ici.
      </span>
    </div>

    <p class="control">
      <span v-on:click="save(null)" class="button is-success" :class="{'is-loading' : saving}">
        <span class="icon">
          <i class="fa fa-bolt"></i>
        </span>
        <span>Mettre à jour</span>
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
};
</script>

