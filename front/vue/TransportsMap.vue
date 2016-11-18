<template>
  <div class="map"></div>
</template>

<style scoped>
.map {
  border: 1px solid #ccc;
  width: 100%;
  height: 600px;
}
</style>

<script>
require('leaflet');
require('leaflet/dist/leaflet.css');
require('leaflet-extra-markers/dist/js/leaflet.extra-markers.min.js');
require('leaflet-extra-markers/dist/css/leaflet.extra-markers.min.css');

module.exports = {
  props : {
    lng : Number,
    lat : Number,
    stops: Array,
    'current_stop' : Object,
  },

  data : function(){
    return {
      map: null,
      markers : {},
      stop_circles : null, // LayerGroup
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

      // Init stop circles
      this.$set(this, 'stop_circles', L.layerGroup().addTo(map));
    });
  },

  watch : {
    stops : function(stops){

      // Display markers for stops
      var bounds = L.latLngBounds();
      var map = this.map;
      var that = this;
      for(var s in stops){
        var stop = this.stops[s];

        var icon = L.ExtraMarkers.icon({
          icon: 'glyphicon-star',
          markerColor: 'blue',
          shape: 'square',
          prefix: 'glyphicon'
        });

        var coords = stop.point.coordinates;
        var point = L.latLng([coords[1], coords[0]]);
        var marker = L.marker(point, {icon: icon,});
        marker.bindPopup(stop.name);
        marker.addTo(map);
        marker.on('click', function(){
          that.$emit('selected_stop', this.stop);
        });
        bounds.extend(point);

        // Link marker to stop
        var markers = this.markers;
        marker.stop = stop;
        markers[stop.id] = marker;
        this.$set(this, 'markers', markers);
      }
      
      // Map fit all points
      map.fitBounds(bounds, {
        padding : [10, 10],
      });
    },

    current_stop : function(stop){
      // Center map around current stop
      if(stop === null)
        return;
      var coords = stop.point.coordinates;
      this.map.setView([coords[1], coords[0]], 17);

      // Show popup
      var marker = this.markers[stop.id];     
      if(marker)
        marker.openPopup();

      // Display line stops as circles
      // unified in a LayerGroup
      var that = this;
      this.stop_circles.clearLayers();
      stop.line_stops.forEach(function(ls, i){
        var coords = ls.point.coordinates;
        var circle = L.circle([coords[1], coords[0]], 4);
        that.stop_circles.addLayer(circle);
      });
    },
  },
}
</script>
