<template>
  <div id="transports" class="row">
    <div class="col-xs-12 col-sm-9">
      <TransportsMap v-bind:lng="lng" v-bind:lat="lat" v-bind:stops="stops"></TransportsMap>
    </div>
    <div class="col-xs-12 col-sm-3 list-group">
      <TransportsStop v-bind:stop="stop" v-for="(stop, i) in stops"/>
    </div>
  </div>
</template>

<script>
var TransportsMap = require('vue/TransportsMap.vue');
var TransportsStop = require('vue/TransportsStop.vue');

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
    };
  },
  components : {
    TransportsMap : TransportsMap,
    TransportsStop : TransportsStop,
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
}
</script>
