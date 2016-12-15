<template>
  <form>
    <p class="control">
      <textarea class="textarea" placeholder="Saisissez du texte à afficher sur votre écran..." v-model="text"></textarea>
    </p>
    <p class="control">
      <span v-on:click="save_text" class="button is-success" :class="{'is-loading' : saving}">
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
  </form>
</template>

<script>
var mixins = require('./mixins.js');

module.exports = {
  mixins : [mixins, ],
  data : function(){
    return {
      text : null,
    };
  },
  mounted : function(){
    // initial text to edit
    this.$set(this, 'text', this.widget.text);
  },
  methods: {
    save_text : function(){
      this.save({
        text : this.text,
      });
    },
  },
};
</script>
