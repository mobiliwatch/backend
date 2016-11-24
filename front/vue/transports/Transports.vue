<template>
  <div class="container-fluid">
    <div class="tile is-ancestor">
      <div class="tile is-parent">
        <div class="tile is-child box is-3">
          <p class="title">{{ stops.length }} arrêts trouvés</p>
          <Stops :stops="stops" :current_stop="current_stop" :line_stops="line_stops" v-on:selected_stop="selected_stop" />
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
        <div class="tile is-child is-6">
          <p class="title">{{ name }}</p>
          <p class="subtitle">{{ address }}</p>
          <Map :point="point" :stops="stops" :current_stop="current_stop" v-on:selected_stop="selected_stop"></Map>

          <div class="notification is-success" v-if="saved">
            <span class="icon">
              <span class="fa fa-check"></span>
            </span>
            Modifications sauvegardées.
          </div>
        </div>
        <div class="tile is-child box">
          <p class="title">Choisir ses arrêts</p>
          <Stop :current_stop="current_stop" :line_stops="line_stops" v-on:toggle_line_stop="toggle_line_stop"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
var Map = require('vue/transports/Map.vue');
var Stop = require('vue/transports/Stop.vue');
var Stops = require('vue/transports/Stops.vue');

module.exports = {
  props : {
    name: String,
    address : String,
    location_id : Number,
    point : Object,
    line_stops_initial : Array,
  },
  data : function(){
    return {
      loading: false,
      saved : false,
      stops : [],
      current_stop : null,
      line_stops : [], // selected by user
      distance : 500,
    };
  },
  components : {
    Map : Map,
    Stop : Stop,
    Stops : Stops,
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
      this.$http.patch(url, data).then(function(){
        this.$set(this, 'saved', true);
        var that = this;
        setTimeout(function(){
          that.$set(that, 'saved', false);
        }, 2000);
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
          return x.distance > y.distance;
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
