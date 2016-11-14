<template>
  <div id="transports" class="row">
    <div class="col-xs-12 col-sm-9">
      <TransportsMap :lng="lng" :lat="lat" :stops="stops" :current_stop="current_stop" v-on:selected_stop="selected_stop"></TransportsMap>

      <form class="form-inline">
        <div class="form-group">
          <div class="input-group">
            <div class="input-group-addon">Distance</div>
            <input type="number" class="form-control" v-model="distance" />
          </div>
        </div>
        <button class="btn btn-primary" v-on:click="load_stops">Search !</button>
      </form>

      <TransportsStop :current_stop="current_stop" :line_stops="line_stops" v-on:toggle_line_stop="toggle_line_stop"/>
    </div>
    <div class="col-xs-12 col-sm-3">
      <TransportsStops :stops="stops" :current_stop="current_stop" :line_stops="line_stops" v-on:selected_stop="selected_stop" />
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
    line_stops_initial : Array,
  },
  data : function(){
    return {
      stops : [],
      current_stop : null,
      line_stops : [], // selected by user
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
    this.$set(this, 'line_stops', this.line_stops_initial);
  },

  methods : {
    selected_stop : function(stop){
      // Save selected stop
      this.$set(this, 'current_stop', stop);
    },

    toggle_line_stop : function(line_stop){
      // Toggle id in local list
      var ls_id = line_stop['id'];
      var index = this.line_stops.indexOf(ls_id);
      if(index > -1){
        this.line_stops.splice(index, 1);
      }else{
        this.line_stops.push(ls_id);
      }

      // Update line stops on backend
      var url = '/api/location/' + this.location_id + '/';
      var data = {
        line_stops : this.line_stops || [],
      };
      this.$http.patch(url, data);
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

        // Sort stops by distance
        var stops = resp.body.sort(function(x, y){
          return x.distance > y.distance;
        });
        this.$set(this, 'stops', stops); // weird

      }).catch(function(resp){
        console.warn('No data', resp);
      });
    },
  },
}
</script>
