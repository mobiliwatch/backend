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
  computed : {
    group : function(){
      return this.$store.state.groups[this.groupId];
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

    toggle_vertical : function(){
      // Toggle vertical orientation
      this.$store.dispatch('update_group', {
        id : this.groupId,
        vertical : !this.group.vertical,
      });
    },
  },
};
</script>

<template>
  <div class="group" v-if="group">
    <div class="control has-addons">
      <span class="button" v-on:click="add_subgroup()">
        <span class="icon is-small">
          <i class="fa fa-object-group"></i>
        </span>
        <span>Ajouter sous-groupe</span>
      </span>
      <span class="button">
        <span class="icon is-small">
          <i class="fa fa-window-maximize"></i>
        </span>
        <span>Ajouter widget</span>
      </span>
      <span class="button" v-on:click="delete_group()">
        <span class="icon is-small">
          <i class="fa fa-trash"></i>
        </span>
        <span>Supprimer groupe</span>
      </span>
      <span class="button" v-on:click="toggle_vertical()">
        <span class="icon is-small">
          <i class="fa fa-arrows-h"></i>
        </span>
        <span>Vertical/Horizontal</span>
      </span>
    </div>

    <div class="tile" :class="{'is-vertical': group.vertical}">
      <Group :groupId="g.id" v-for="g in group.groups" />

      <div class="tile is-parent" v-for="w in group.widgets">
        <Widget :widgetId="w" />
      </div>
    </div>
  </div>
</template>

<style scoped>
div.group {
  border: 1px solid #EEE;
  padding-top: 5px;
  margin-left: 5px;
  margin-right: 5px;
  margin-bottom: 5px;
}

div.tile, div.tile.is-parent {
  height: 90%;
}

div.control.has-addons {
  height: 30px;
  margin-left: 10px;
}
</style>
