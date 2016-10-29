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

var transports = function(elt, lat, lng){
  new Vue({
    el: elt,
    data : {
      lng : lng,
      lat : lat,
    },
    mounted : function(){
      console.log('Start', this);
    },
  });
};
