<template>
  <div class="tile is-parent" v-if="widget">
    <article class="tile is-child box">
      <div class="level">
        <div class="level-left">
          <h1 class="level-item title">
            {{ types[widget.type].title }}
          </h1>
        </div>
        <div class="level-right">
          <span class="button level-item" v-on:click="open()">
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
            <button class="delete" v-on:click="close()"></button>
          </header>
          <section class="modal-card-body">
            <div v-for="(meta, type) in types" v-if="type != widget.type" class="columns is-multiline widget-description">
              <div class="column is-8">
                <h5 class="title is-5">{{ meta.title }}</h5>
              </div>
              <div class="column is-4 has-text-right">
                <span class="button is-primary" v-on:click="replace(type)" :disabled="replacing">
                  <span class="icon is-small">
                    <span class="fa fa-check"></span>
                  </span>
                  <span>Utiliser ce widget</span>
                </span>
              </div>
              <div class="column is-12">
                {{ meta.description }}
              </div>
            </div>
          </section>
          <footer class="modal-card-foot">
            <a class="button" v-on:click="close()">Annuler</a>
          </footer>
        </div>
      </div>
    </article>
  </div>
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
    open : function(){
      this.$set(this, 'modal', true);
    },
    close : function(){
      this.$set(this, 'modal', false);
    },
    replace : function(type){
      // Replace current widget with a new type
      var that = this;
      this.$set(this, 'replacing', true);
      this.$store.dispatch('replace_widget', {
        id : this.widgetId,
        type : type,
        group : this.groupId,
      }).then(function(){
        that.close();
        that.$set(that, 'replacing', false);
      });
    },
  },
  data : function(){
    return {
      modal : false,
      replacing : false,
      types : {
        'LocationWidget' : {
          title : 'Prochains passages',
          description : 'Ce widget vous permet de savoir quand partir du lieu vers un arrêt sélectionné afin de ne plus jamais attendre vos transports en commun !',
        },
        'ClockWidget' : {
          title : 'Horloge',
          description : 'Afichez une horloge (date et heure) sur votre écran avec ce widget.',
        },
        'WeatherWidget' : {
          title : 'Météo',
          description : 'Ce widget affiche la tendance météo de la journée de la ville choisie, ainsi que l\'indice de pollution.',
        },
        'DisruptionWidget' : {
          title : 'Perturbations',
          description : 'Avec ce widget vous aurez accès à toutes les perturbations en cours pour les lignes sélectionnées dans votre lieu (alertes pollutions, promotions commerciales, perturbations techniques, etc.)',
        },
        'NoteWidget' : {
          title : 'Notes',
          description : 'Avec ce widget vous pouvez laisser un message sur l\'écran: une liste de courses, un memo, un gentil mot...',
        },
      },
    };
  },
};
</script>

<style scoped>
.widget-description {
  border-bottom: 1px solid #F1F1F1;
  padding-bottom: 3px;
  margin-bottom: 12px;
}
</style>
