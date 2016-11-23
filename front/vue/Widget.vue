<script>
module.exports = {
  props : {
    widgetId : String,
  },
  data : function(){
    return {};
  },
};
</script>

<template>

  <div class="tile is-parent">
    <article class="tile is-child notification is-info">
      <div class="content">
        <h1>{{ widgetId }}</pre>

      </div>
    </article>
  </div>
</template>
