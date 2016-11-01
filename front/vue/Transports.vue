<template>
  <div id="transports" class="row">
    <div class="col-xs-12 col-sm-9">
      <TransportsMap v-bind:lng="lng" v-bind:lat="lat" v-bind:stops="stops" v-bind:current_stop="current_stop"></TransportsMap>
    </div>
    <div class="col-xs-12 col-sm-3">
      <TransportsStops v-bind:stops="stops" v-bind:current_stop="current_stop" v-on:selected_stop="selected_stop" />
    </div>
  </div>
</template>

<script>
var TransportsMap = require('vue/TransportsMap.vue');
var TransportsStops = require('vue/TransportsStops.vue');

module.exports = {
  props : {
    location_id : Number,
    lat : Number,
    lng : Number,
    distance : {
      type : Number,
      default : 500,
    },
  },
  data : function(){
    return {
      stops : [],
      current_stop : null,
    };
  },
  components : {
    TransportsMap : TransportsMap,
    TransportsStops : TransportsStops,
  },
  mounted : function(){

    // Load nearest stops
    var url = '/api/location/' + this.location_id + '/stops/';
    var options = {
      params : {
        'distance' : this.distance,
      }
    };
    this.$http.get(url, options).then(function(resp){
      this.$set(this, 'stops', resp.body); // weird

    }).catch(function(resp){
      console.warn('No data', resp);
    });
  },

  methods : {
    'selected_stop' : function(stop){
      // Save selected stop
      this.$set(this, 'current_stop', stop);
    },
  },
}
</script>
