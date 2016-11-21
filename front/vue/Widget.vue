<script>
module.exports = {
  props : {
    widget : Object,
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
        <pre>
          {{ widget }}
        </pre>

      </div>
    </article>
  </div>
</template>
