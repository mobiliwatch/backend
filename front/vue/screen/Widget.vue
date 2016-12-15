<template>
  <article class="tile is-child box" v-if="widget">
    <div class="level">
      <div class="level-left">
        <h1 class="level-item title">
          {{ types[widget.type].title }}
        </h1>
      </div>
      <div class="level-right">
        <span class="button level-item" v-on:click="toggle_modal()">
          <span class="icon is-small">
            <span class="fa fa-pencil"></span>
          </span>
          <span>Changer</span>
        </span>
      </div>
    </div>
    <div class="content">
      <Note v-if="widget.type == 'NoteWidget'" :widgetId="widget.id" />
      <Weather v-if="widget.type == 'WeatherWidget'" :widgetId="widget.id" />
      <Clock v-if="widget.type == 'ClockWidget'" :widgetId="widget.id" />
      <LocationWidget v-if="widget.type == 'LocationWidget'" :widgetId="widget.id" />
      <Disruption v-if="widget.type == 'DisruptionWidget'" :widgetId="widget.id" />
    </div>
    <div class="modal" :class="{'is-active': modal}">
      <div class="modal-background"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Changer le widget</p>
          <button class="delete" v-on:click="toggle_modal()"></button>
        </header>
        <section class="modal-card-body">
          <div v-for="(meta, type) in types" v-if="type != widget.type">
            <h5 class="title is-5">{{ meta.title }}</h5>
            <p>{{ meta.description }}</p>
            <span class="button is-primary" v-on:click="replace(type)">
              <span class="icon is-small">
                <span class="fa fa-check"></span>
              </span>
              <span>Utiliser</span>
            </span>
            <hr />
          </div>
        </section>
        <footer class="modal-card-foot">
          <a class="button" v-on:click="toggle_modal()">Annuler</a>
        </footer>
      </div>
    </div>
  </article>
</template>

<script>
var mixins = require('./widgets/mixins.js');
var Note = require('./widgets/Note.vue');
var Weather = require('./widgets/Weather.vue');
var Clock = require('./widgets/Clock.vue');
var LocationWidget = require('./widgets/Location.vue');
var Disruption = require('./widgets/Disruption.vue');

module.exports = {
  mixins : [mixins, ],
  components : {
    Note : Note,
    Weather : Weather,
    Clock : Clock,
    LocationWidget : LocationWidget, // reserved word location
    Disruption : Disruption,
  },
  methods : {
    toggle_modal : function(){
      this.$set(this, 'modal', !this.modal);
    },
    replace : function(type){
      // Replace current widget with a new type
      this.$store.dispatch('replace_widget', {
        id : this.widgetId,
        type : type,
      });
    },
  },
  data : function(){
    return {
      modal : false,
      types : {
        'LocationWidget' : {
          title : 'Prochains passages',
          description : '...',
        },
        'ClockWidget' : {
          title : 'Horloge',
          description : '...',
        },
        'WeatherWidget' : {
          title : 'Météo',
          description : '...',
        },
        'DisruptionWidget' : {
          title : 'Perturbations',
          description : '...',
        },
        'NoteWidget' : {
          title : 'Notes',
          description : '...',
        },
      },
    };
  },
};
</script>
