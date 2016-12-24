<template>
  <div>
    <span class="button is-info" v-on:click="toggle()">
      <span class="icon is-small">
        <span class="fa fa-plus"></span>
      </span>
      <span>Créer un écran</span>
    </span>

    <div class="modal" :class="{'is-active' : active }">
      <div class="modal-background"></div>
      <div class="modal-card">
        <header class="modal-card-head">
          <p class="modal-card-title">Créer un nouvel écran</p>
          <button class="delete" v-on:click="toggle()"></button>
        </header>
        <section class="modal-card-body">

          <div class="control">
            <label class="label">Choisir un mode d'affichage</label>
            <div class="columns" v-if="templates">
              <div class="column is-3" v-for="t in templates">
                <img :src="t.preview" :alt="t.slug" />
                <label class="label">
                  <input type="radio" v-model="template" :value="t.id" />
                  {{ t.name }}
                </label>
              </div>
            </div>
          </div>

          <div class="control">
            <label class="label">Nommer l'écran</label>
            <input type="text" class="input" v-model="name" />
          </div>

        </section>
        <footer class="modal-card-foot">
          <a class="button is-primary" v-on:click="create()" :disabled="!template || !name">Créer</a>
          <span class="button" v-on:click="toggle()">Annuler</span>
        </footer>
      </div>
  </div>
</template>

<script>
module.exports = {
  props : {
    location : Number,
  },
  data : function(){
    return {
      name : '',
      active : false,
      template : null,
      templates : null,
    };
  },
  mounted : function(){
    this.$http.get('/api/template/').then(function(resp){
      this.$set(this, 'templates', resp.body);
    });
  },
  methods : {
    toggle : function(){
      this.$set(this, 'active', !this.active);
    },
    create : function(){
      var data = {
        location : this.location,
        template : this.template,
        name : this.name,
      };
      this.$http.post('/api/template/', data).then(function(resp){
        // Redirect to frontend
        window.location.href = resp.body.frontend_url;
      });
    },
  },
};
</script>
