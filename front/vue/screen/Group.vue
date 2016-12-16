<script>
var Widget = require('./Widget.vue');

module.exports = {
  components : {
    Widget : Widget,
  },
  beforeCreate: function () {
    this.$options.components.Group = require('./Group.vue')
  },
  props : {
    groupId : Number,
  },
  data : function(){
    return {
      editing : false,
    };
  },
  computed : {
    group : function(){
      return this.$store.state.groups[this.groupId];
    },
    editor : function(){
      return this.$store.state.editor;
    },
  },
  methods : {
    add_subgroup : function(){
      // Add a sub-group to current one
      this.$store.dispatch('add_subgroup', {
        id : this.groupId,
      });
    },

    delete_group : function(){
      // Delete current group
      this.$store.dispatch('delete_group', {
        id : this.groupId,
      });
    },

    add_widget : function(widget_type){
      // Add a new widget to the group
      this.$store.dispatch('add_widget', {
        group : this.groupId,
        widget_type : widget_type,
      });
    },

    toggle_vertical : function(){
      // Toggle vertical orientation
      this.$store.dispatch('update_group', {
        id : this.groupId,
        vertical : !this.group.vertical,
      });
    },
    
    toggle_editing : function(){
      this.$set(this, 'editing', !this.editing);
    },
  },
};
</script>

<template>
  <div class="group" v-if="group" :class="{'tile' : editor == 'normal'}">
    <p v-if="!editing && editor == 'advanced'">
      <span class="button is-info" v-on:click="toggle_editing()">
        <span class="icon is-small">
          <i class="fa fa-pencil"></i>
        </span>
        <span>Editer groupe/widget</span>
      </span>
    </p>

    <nav class="panel" v-if="editing && editor == 'advanced'">
      <a class="panel-block" v-on:click="add_widget('Weather')">
        <span class="panel-icon is-small">
          <i class="fa fa-window-maximize"></i>
        </span>
        <span>Ajouter widget météo</span>
      </a>
      <a class="panel-block" v-on:click="add_widget('Location')">
        <span class="panel-icon is-small">
          <i class="fa fa-window-maximize"></i>
        </span>
        <span>Ajouter widget transports</span>
      </a>
      <a class="panel-block" v-on:click="add_widget('Disruption')">
        <span class="panel-icon is-small">
          <i class="fa fa-window-maximize"></i>
        </span>
        <span>Ajouter widget perturbations</span>
      </a>
      <a class="panel-block" v-on:click="add_widget('Clock')">
        <span class="panel-icon is-small">
          <i class="fa fa-window-maximize"></i>
        </span>
        <span>Ajouter widget horloge</span>
      </a>
      <a class="panel-block" v-on:click="add_widget('Note')">
        <span class="panel-icon is-small">
          <i class="fa fa-window-maximize"></i>
        </span>
        <span>Ajouter widget notes</span>
      </a>
      <a class="panel-block" v-on:click="add_subgroup()">
        <span class="panel-icon is-small">
          <i class="fa fa-object-group"></i>
        </span>
        <span>Ajouter sous-groupe</span>
      </a>
      <a class="panel-block" v-on:click="delete_group()">
        <span class="panel-icon is-small">
          <i class="fa fa-trash"></i>
        </span>
        <span>Supprimer groupe</span>
      </a>
      <a class="panel-block" v-on:click="toggle_vertical()" v-if="group.vertical">
        <span class="panel-icon is-small">
          <i class="fa fa-arrows-h"></i>
        </span>
        <span>Affichage horizontal</span>
      </a>
      <a class="panel-block" v-on:click="toggle_vertical()" v-else>
        <span class="panel-icon is-small">
          <i class="fa fa-arrows-v"></i>
        </span>
        <span>Affichage vertical</span>
      </a>

      <div class="panel-block">
        <button class="button is-primary is-outlined is-fullwidth" v-on:click="toggle_editing()">
          Fermer
        </button>
      </div>
    </nav>

    <div class="tile" :class="{'is-vertical': group.vertical}">
      <Group :groupId="g.id" v-for="g in group.groups" />

      <div class="tile is-parent" v-for="w in group.widgets">
        <Widget :widgetId="w" :groupId="groupId" />
      </div>
    </div>
  </div>
</template>

<style scoped lang="sass">
div.editor.advanced {
  div.group {
    border: 1px solid #EEE;
    padding-top: 5px;
    margin-left: 5px;
    margin-right: 5px;
    margin-bottom: 5px;
  }

  div.tile {
    height: 90%;

  }

  nav {
    background: #EEE;
  }
}
</style>
