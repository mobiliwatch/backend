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
        <div class="tile is-child is-6" v-if="location">
          <div class="level top">
            <div class="level-left">
              <div class="level-item">
                <p class="title">{{ location.name }}</p>
                <p class="heading">{{ location.address }} - {{ location.city.name }}</p>
              </div>
            </div>

            <div class="level-right">
              <p class="level-item" v-for="screen in location.screens">
                <a :href="'/screen/' + screen.slug" class="button is-outlined is-success">
                  <span class="icon is-small">
                    <span class="fa fa-desktop"></span>
                  </span>
                  <span>{{ screen.name }}</span>
                </a>
              </p>
            </div>
          </div>
          <TransportsMap :name="location.name" :point="location.point" :stops="stops" :path="path" :current_stop="current_stop" v-on:selected_stop="selected_stop"></TransportsMap>

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
var TransportsMap = require('vue/transports/Map.vue');
var Stop = require('vue/transports/Stop.vue');
var Stops = require('vue/transports/Stops.vue');

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
    };
  },
  components : {
    TransportsMap : TransportsMap,
    Stop : Stop,
    Stops : Stops,
  },
  mounted : function(){
    this.load_location();
    this.load_stops();
  },

  methods : {
    selected_stop : function(stop){
      // Save selected stop
      this.$set(this, 'current_stop', stop);

      // Load distance for this stop
      var url = '/api/location/' + this.location_id + '/distance/' + stop.id + '/';
      this.$http.get(url).then(function(resp){
        this.$set(this, 'path', resp.body.geometry);
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

<style scoped>

div.tile div.level.top {
  padding: 0 5px;
  margin-bottom: 0px;
}
</style>
