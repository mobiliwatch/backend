<template>

  <div class="tile is-parent">
    <article class="tile is-child box">
      <div class="content">

        <Note v-if="widget.type == 'NoteWidget'" :widgetId="widget.id" />

        <div v-if="widget.type == 'WeatherWidget'">
          <h1 class="title">Météo</h1>
          <div class="notification is-info">
            <span class="icon">
              <span class="fa fa-bolt"></span>
            </span>
            <span>
              Les prévisions météo s'afficheront ici.
            </span>
          </div>
        </div>

        <div v-if="widget.type == 'ClockWidget'">
          <h1 class="title">Horloge</h1>
          <div class="notification is-info">
            <span class="icon">
              <span class="fa fa-clock-o"></span>
            </span>
            <span>
              Une horloge s'affichera ici.
            </span>
          </div>
        </div>

        <div v-if="widget.type == 'LocationWidget'">
          <h1 class="title">Prochains passages</h1>
          <div class="notification is-info">
            <span class="icon">
              <span class="fa fa-bus"></span>
            </span>
            <span>
              Les horaires des prochains de vos arrêts choisis s'afficheront ici.
            </span>
          </div>
        </div>

      </div>
    </article>
  </div>
</template>

<script>
var mixins = require('./widgets/mixins.js');
var Note = require('./widgets/Note.vue');

module.exports = {
  mixins : [mixins, ],
  components : {
    Note : Note,
  },
  data : function(){
    return {};
  },
};
</script>
