<template>
  <form>
    <p class="control">
      <label class="label">Mode à afficher:</label>
      <select v-model="mode">
        <option :value="'timeline'">Votre flux twitter</option>
        <option :value="'user_tweets'">Les tweets que vous publiez</option>
        <option :value="'search'">Recherche twitter (hashtag)</option>
      </select>
    </p>
    <p class="control" v-if="mode == 'search'">
      <label class="label">Critères de la recherche:</label>
      <input type="text" class="input" :class="{'is-danger': !search_terms}" placeholder="Twitter #hashtag" v-model="search_terms"/>
      <span class="help is-danger" v-if="!search_terms">Veuillez renseigner ce champ</span>
    </p>
    <p class="control">
      <span v-on:click="save_text" class="button is-success" :class="{'is-loading' : saving}" :disabled="mode == 'search' && !search_terms">
        <span class="icon">
          <i class="fa fa-check"></i>
        </span>
        <span>Enregistrer</span>
      </span>
      <span v-on:click="delete_widget" class="button is-danger" :class="{'is-loading' : deleting}" v-if="editor == 'advanced'">
        <span class="icon">
          <i class="fa fa-trash"></i>
        </span>
        <span>Supprimer</span>
      </span>
    </p>
  </form>
</template>

<script>
var mixins = require('./mixins.js');

module.exports = {
  mixins : [mixins, ],
  data : function(){
    return {
      mode: null,
      search_terms: null,
    };
  },
  mounted : function(){
    // initial values
    this.$set(this, 'mode', this.widget.mode);
    this.$set(this, 'search_terms', this.widget.search_terms);
  },
  methods: {
    save_text : function(){
      this.save({
        mode : this.mode,
        search_terms : this.search_terms,
      });
    },
  },
};
</script>
