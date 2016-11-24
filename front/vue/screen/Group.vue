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
    widgets : Array,
    group : Object,
  },
  data : function(){
    return {};
  },
};
</script>

<template>
  <div class="group tile" :class="{'is-vertical': group.vertical}">

    <Group :group="g" :widgets="widgets" v-for="g in group.groups" />

    <div class="tile" v-for="w in group.widgets">
      <Widget :widgetId="w" />
    </div>

<!--
    <div class="control is-grouped">
      <p class="control has-addons">
        <button class="button">
          <span class="icon is-small">
            <i class="fa fa-plus"></i>
          </span>
        <span>Ajouter un widget</span>
        </button>
      </p>
      <p class="control has-addons">
        <button class="button">
          <span class="icon is-small">
            <i class="fa fa-align-left"></i>
          </span>
        <span>Left</span>
        </button>
      </p>
    </div>
-->

  </div>
</template>
