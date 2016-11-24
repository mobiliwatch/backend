<template>
  <form>
    <h1 class="title">Notes</h1>
    <p class="control">
      <textarea class="textarea" placeholder="Saisissez du texte à afficher sur votre écran..." v-model="text"></textarea>
    </p>
    <p class="control">
      <span v-on:click="save" class="button is-success" :class="{'is-loading' : saving}">
        <span class="icon">
          <i class="fa fa-check"></i>
        </span>
        <span>Enregistrer</span>
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
      saving : false,
    };
  },
  mounted : function(){
    // initial text to edit
    this.$set(this, 'text', this.widget.text);
  },
  methods: {
    save : function(){
      this.$set(this, 'saving', true);
      var that = this;
      this.$store.dispatch('update_widget', {
        id : this.widget.id,
        text : this.text,
      }).then(function(){
        that.$set(that, 'saving', false);
      }).catch(function(){
        that.$set(that, 'saving', false);
      });
    },
  },
};
</script>
