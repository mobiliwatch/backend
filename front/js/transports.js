Vue.component('transports-map', {
  template: '<div class="map"></div>',

  props : {
    lng : Number,
    lat : Number,
    stops: Array,
  },

  data : function(){
    return {
      map: null,
    }
  },

  mounted : function(){

    // Setup base map
    this.$nextTick(function () {
      var map = L.map(this.$el).setView([this.lng, this.lat], 16);

      // Use grayscale tiles
      L.tileLayer('http://{s}.grayscale.osm.maptiles.xyz/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
          '<a href="https://maptiles.xyz">Maptiles.xyz</a>'
      }).addTo(map);

      // Add a marker for location
      var icon = L.ExtraMarkers.icon({
        icon: 'glyphicon-home',
        markerColor: 'green',
        shape: 'square',
        prefix: 'glyphicon'
      });

      L.marker([this.lng, this.lat], {icon: icon,}).addTo(map);

      this.$set(this, 'map', map);
    });
  },

  watch : {
    stops : function(stops){
      var map = this.map;
      for(var s in stops){
        var stop = this.stops[s];

        var icon = L.ExtraMarkers.icon({
          icon: 'glyphicon-star',
          markerColor: 'blue',
          shape: 'square',
          prefix: 'glyphicon'
        });

        var coords = stop.point.coordinates;
        L.marker([coords[1], coords[0]], {icon: icon,}).addTo(map);
      }
    },
  },
});

Vue.component('transports-stop', {
  template : '#transports-stop',

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
});

var transports = function(elt, location_id, lat, lng){
  new Vue({
    el: elt,
    data : {
      location_id : location_id,
      lng : lng,
      lat : lat,
      distance : 500, // default distance
      stops : [],
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
  });
};
