<template>
  <div id="transports" class="row">
    <div class="col-xs-12 col-sm-9">
      <TransportsMap v-bind:lng="lng" v-bind:lat="lat" v-bind:stops="stops" v-bind:current_stop="current_stop" v-on:selected_stop="selected_stop"></TransportsMap>

      <form class="form-inline">
        <div class="form-group">
          <div class="input-group">
            <div class="input-group-addon">Distance</div>
            <input type="number" class="form-control" v-model="distance" />
          </div>
        </div>
        <button class="btn btn-primary" v-on:click="load_stops">Search !</button>
      </form>

      <TransportsStop v-bind:current_stop="current_stop" />
    </div>
    <div class="col-xs-12 col-sm-3">
      <TransportsStops v-bind:stops="stops" v-bind:current_stop="current_stop" v-on:selected_stop="selected_stop" />
    </div>
  </div>
</template>

<script>
var TransportsMap = require('vue/TransportsMap.vue');
var TransportsStop = require('vue/TransportsStop.vue');
var TransportsStops = require('vue/TransportsStops.vue');

module.exports = {
  props : {
    location_id : Number,
    lat : Number,
    lng : Number,
  },
  data : function(){
    return {
      stops : [],
      current_stop : null,
      distance : 500,
    };
  },
  components : {
    TransportsMap : TransportsMap,
    TransportsStop : TransportsStop,
    TransportsStops : TransportsStops,
  },
  mounted : function(){
    this.load_stops();
  },

  methods : {
    selected_stop : function(stop){
      // Save selected stop
      this.$set(this, 'current_stop', stop);
    },

    load_stops : function(evt){
      if(evt)
        evt.preventDefault();

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
  },
}
</script>
