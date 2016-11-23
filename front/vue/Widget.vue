<script>
module.exports = {
  props : {
    widgetId : String,
  },
  data : function(){
    return {};
  },
  computed : {
    widget : function(){
      return this.$store.state.widgets[this.widgetId];
    },
  }
};
</script>

<template>

  <div class="tile is-parent">
    <article class="tile is-child notification is-info">
      <div class="content">
        <h1 class="title">{{ widget.type }}</h1>
        <h5 class="subtitle">{{ widget.id }}</h5>
      </div>
    </article>
  </div>
</template>
