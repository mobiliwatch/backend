<template>
  <div class="container-fluid">
    <div class="tile is-ancestor">
      <div class="tile is-parent">
        <div class="tile is-child box is-3">
          <p class="title">{{ stops.length }} arrêts trouvés</p>
          <div id="stops" :style="{height : heights.stops + 'px'}">
            <Stops :stops="stops" :current_stop="current_stop" v-on:selected_stop="selected_stop" />
          </div>
          <hr />
          <div>
            <label class="label">Changer la distance de recherche des arrêts</label>
            <p class="control has-addons">
              <input type="number" class="input" v-model="distance" />
              <button class="button is-info" v-bind:class="{'is-loading':loading}" v-on:click="load_stops">
                Chercher des arrêts
              </button>
            </p>
          </div>
        </div>
        <div class="tile is-child is-6" v-if="location">
          <div class="level top">
            <div class="level-left">
              <div class="level-item">
                <p class="title">{{ location.name }}</p>
                <p class="heading">{{ location.address }} - {{ location.city.name }}</p>
              </div>
            </div>

            <div class="level-right">
              <div class="notification is-success" v-if="saved">
                <span class="icon">
                  <span class="fa fa-check"></span>
                </span>
                Modifications sauvegardées.
              </div>
            </div>
          </div>
          <TransportsMap :height="heights.map" :name="location.name" :point="location.point" :stops="stops" :path="path" :current_stop="current_stop" v-on:selected_stop="selected_stop"></TransportsMap>

          <TransportsSummary :location="location.id" :screens="location.screens" :stops="stops" :line_stops="line_stops" v-on:toggle_line_stop="toggle_line_stop"/>
        </div>
        <div class="tile is-child box">
          <Stop :current_stop="current_stop" :line_stops="line_stops" v-on:toggle_line_stop="toggle_line_stop"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var _ = require('lodash');
var TransportsMap = require('vue/transports/Map.vue');
var Stop = require('vue/transports/Stop.vue');
var Stops = require('vue/transports/Stops.vue');
var Summary = require('vue/transports/Summary.vue');

module.exports = {
  props : {
    location_id : Number,
  },
  data : function(){
    return {
      location: null,
      loading: false,
      saved : false,
      stops : [],
      path : null,
      current_stop : null,
      line_stops : [], // selected by user
      distance : 500,
      heights : {
        stops : 400, // default height
        map : 400,
      },
    };
  },
  components : {
    TransportsMap : TransportsMap,
    Stop : Stop,
    Stops : Stops,
    TransportsSummary : Summary,
  },
  mounted : function(){
    this.load_location();
    this.load_stops();

    // Calc heights
    this.$set(this, 'heights', {
      stops : window.innerHeight - 270,
      map : window.innerHeight - 180,
    });
  },

  methods : {
    selected_stop : function(stop){
      // Save selected stop
      this.$set(this, 'current_stop', stop);
      if(stop.trip){
        // avoid repeated requests
        this.$nextTick(function(){
          this.$set(this, 'path', stop.trip.geometry);
        });
        return;
      }

      // Find stop index
      var index = _.findIndex(this.stops, function(s){
        return s.id == stop.id;
      });

      // Load trip for this stop
      var url = '/api/location/' + this.location_id + '/distance/' + stop.id + '/';
      this.$http.get(url).then(function(resp){
        // Save currently display path
        this.$set(this, 'path', resp.body.geometry);

        // Update trip on stop
        stop.trip = resp.body;
        var stops = _.clone(this.stops);
        stops[index] = stop;
        this.$set(this, 'stops', stops);
      });
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
      this.$http.patch(url, data).then(function(){
        this.$set(this, 'saved', true);
        var that = this;
        setTimeout(function(){
          that.$set(that, 'saved', false);
        }, 2000);
      });
    },

    // Load location data
    load_location : function(){
      var url = '/api/location/' + this.location_id + '/';
      this.$http.get(url).then(function(resp){
        this.$set(this, 'location', resp.body);

        var line_stops = [];
        this.location.line_stops.forEach(function(ls){
          line_stops.push(ls);
        });
        this.$set(this, 'line_stops', line_stops);
      }).catch(function(resp){
        console.warn('No data', resp);
      });
    },
    load_stops : function(evt){
      if(evt)
        evt.preventDefault();

      this.$set(this, 'loading', true);

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
          return x.approximate_distance > y.approximate_distance;
        });
        this.$set(this, 'stops', stops); // weird
        this.$set(this, 'loading', false);

      }).catch(function(resp){
        this.$set(this, 'loading', false);
        console.warn('No data', resp);
      });
    },
  },
}
</script>

<style>

div.tile div.level.top {
  padding: 0 5px;
  margin-bottom: 0px;
}

div#stops {
  height: 400px;
  overflow-y: scroll;
}
</style>
