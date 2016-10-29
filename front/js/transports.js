Vue.component('transports-map', {
  template: '<div class="map"></div>',

  props : {
    lng : Number,
    lat : Number,
  },

  data : function(){
    return {
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
      var redMarker = L.ExtraMarkers.icon({
        icon: 'glyphicon-home',
        markerColor: 'green',
        shape: 'square',
        prefix: 'glyphicon'
      });

      L.marker([this.lng, this.lat], {icon: redMarker,}).addTo(map);
    });
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
      stops : null,
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
        this.stops = resp.json;

      }).catch(function(resp){
        console.warn('No data', resp);
      });
    },
  });
};
