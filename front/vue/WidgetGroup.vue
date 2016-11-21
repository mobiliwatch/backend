<script>
var Widget = require('./Widget.vue');

module.exports = {
  components : {
    Widget : Widget,
  },
  beforeCreate: function () {
    this.$options.components.Group = require('./WidgetGroup.vue')
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
      <Widget :widget="widgets[w]" />
    </div>

  </div>
</template>
