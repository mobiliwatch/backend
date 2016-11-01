<template>
  <div href="#" class="list-group-item" v-on:click="selected">
    <h5 class="list-group-item-heading">{{ stop.name }}</h5>
    <div class="list-group-item-text">
      <ul>
        <li v-for="(line_stop, i) in stop.line_stops">
          {{ line_stop.line.mode}} {{ line_stop.line.name }}
          > {{ line_stop.direction.name }}
        </li>
      </ul>
    <div>
  </div>
</template>

<script>
module.exports = {
  props : {
    'stop' : {
      type : Object,
      required : true,
    }
  },

  data : function(){
    return {
    }
  },

  methods : {
    selected : function(evt){
      console.log('Selected stop', this);
    },
  },
}
</script>
