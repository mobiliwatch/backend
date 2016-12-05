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
  data : function(){
    return {
      show_modal : false,
    };
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
  methods : {
    toggle_modal : function(){
      this.$set(this, 'show_modal', !this.show_modal);
    },
    delete_stop : function(line_stop){
console.log('ls', line_stop);
      this.$emit('toggle_line_stop', line_stop);
    },
  },
}
</script>

<template>
  <div>

    <div class="modal" :class="{'is-active' : show_modal}">
      <div class="modal-background"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">
            {{ line_stops_list.length }} arrêts sélectionnés
          </p>
          <button class="delete" v-on:click="toggle_modal()"></button>
        </header>

        <section class="modal-card-body">
          <div v-if="line_stops_list.length">
            <p>Tous ces arrêts seront affichés sur vos écrans :</p>

            <table class="table">
              <thead>
                <tr>
                  <th>Arrêt</th>
                  <th>Ligne</th>
                  <th>Direction</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ls in line_stops_list">
                  <td>{{ ls.stop.name }}</td>
                  <td>{{ ls.line.mode }} {{ ls.line.name }}</td>
                  <td>{{ ls.direction.name }}</td>
                  <td>
                    <span class="button is-danger is-outlined" title="Supprimer" v-on:click="delete_stop(ls)">
                      <span class="icon is-small">
                        <span class="fa fa-trash"></span>
                      </span>
                      <span>Supprimer</span>
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>

          </div>

          <p class="no-selection" v-else>
            <span class="icon is-small">
              <span class="fa fa-bus"></span>
            </span>
            Aucune ligne sélectionée.
          </p>
        </section>
        <footer class="modal-card-foot">
          <a :href="'/screen/' + screen.slug" class="button is-success" v-for="screen in screens">
            <span class="icon is-small">
              <span class="fa fa-desktop"></span>
            </span>
            <span>Écran {{ screen.name }}</span>
          </a>
          <a href="/screen/new/" class="button is-info">
            <span class="icon is-small">
              <span class="fa fa-plus"></span>
            </span>
            <span>Ajouter un écran</span>
          </a>
          <span class="button" v-on:click="toggle_modal()">
            Annuler
          </span>
        </footer>
      </div>
    </div>

    <div v-if="line_stops_list.length" class="level">
      <p class="level-left">
        <p class="level-item">
          <span>Vos écrans</span>
          <a :href="'/screen/' + screen.slug" v-for="screen in screens">
            <span class="icon is-small">
              <span class="fa fa-desktop"></span>
            </span>
            <span>{{ screen.name }}</span>
          </a>
          <span>utiliseront vos arrêts.</span>
        </p>
      </p>
      <p class="level-right">
        <span class="button is-success level-item" v-on:click="toggle_modal()">
          <span class="icon is-small">
            <span class="fa fa-bus"></span>
          </span>
          <span>Voir les arrêts sélectionnés</span>
        </span>
        <a href="/screen/new/" class="button is-info level-item">
          <span class="icon is-small">
            <span class="fa fa-plus"></span>
          </span>
          <span>Ajouter un écran</span>
        </a>
      </p>
    </div>
    <div class="level" v-else>
      <div class="level-item">
        <span class="icon">
          <span class="fa fa-info"></span>
        </span>
        Veuillez sélectionner des arrêts de bus, tramway, autocar pour les utiliser dans vos écrans.
      </div>
    </div>

  </div>
</template>

<style scoped>
div.level {
  margin-top: 5px;
  padding: 0 8px;
}
</style>
