<template>
  <div class="map"></div>
</template>

<script>
require('leaflet');
//require('Leaflet.extra-markers');

module.exports = {
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
/*
      var icon = L.ExtraMarkers.icon({
        icon: 'glyphicon-home',
        markerColor: 'green',
        shape: 'square',
        prefix: 'glyphicon'
      });
*/

      //L.marker([this.lng, this.lat], {icon: icon,}).addTo(map);
      L.marker([this.lng, this.lat]).addTo(map);

      this.$set(this, 'map', map);
    });
  },

  watch : {
    stops : function(stops){
      var map = this.map;
      for(var s in stops){
        var stop = this.stops[s];

/*
        var icon = L.ExtraMarkers.icon({
          icon: 'glyphicon-star',
          markerColor: 'blue',
          shape: 'square',
          prefix: 'glyphicon'
        });
*/

        var coords = stop.point.coordinates;
        //L.marker([coords[1], coords[0]], {icon: icon,}).addTo(map);
        L.marker([coords[1], coords[0]]).addTo(map);
      }
    },
  },
}
</script>
