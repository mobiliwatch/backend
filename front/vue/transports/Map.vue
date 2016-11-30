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
    name: String,
    point: Object,
    path: Object,
    stops: Array,
    'current_stop' : Object,
  },

  data : function(){
    return {
      map: null,
      bounds : L.latLngBounds(),
      markers : {},
      path_layer : null,
      stop_circles : null, // LayerGroup
    }
  },

  mounted : function(){

    // Setup base map
    this.$nextTick(function () {
      var map = L.map(this.$el).setView(this.point.coordinates, 16);
      this.$set(this, 'map', map);

      // Use grayscale tiles
      L.tileLayer('http://{s}.grayscale.osm.maptiles.xyz/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
          '<a href="https://maptiles.xyz">Maptiles.xyz</a>'
      }).addTo(map);

      // Init layers
      this.$set(this, 'stop_circles', L.layerGroup().addTo(this.map));
      this.$set(this, 'path_layer', L.geoJSON().addTo(this.map));
    });
  },

  methods : {
    add_marker : function(name, coords, icon_name, icon_color){
      var icon = L.ExtraMarkers.icon({
        icon: icon_name,
        markerColor: icon_color,
        shape: 'square',
        prefix: 'fa'
      });
      var point = L.latLng([coords[1], coords[0]]);
      var marker = L.marker(point, {icon: icon,});
      marker.bindPopup(name);
      marker.addTo(this.map);
      this.bounds.extend(point);

      return marker;
    },
  },

  watch : {
    stops : function(stops){

      // Display markers for stops
      var map = this.map;
      var that = this;
      var markers = [];

      for(var s in stops){
        // Build marker for each stop
        var stop = this.stops[s];
        var marker = this.add_marker(stop.name, stop.point.coordinates, 'fa-star', 'blue');
        marker.on('click', function(){
          that.$emit('selected_stop', this.stop);
        });

        // Link marker to stop
        marker.stop = stop;
        markers[stop.id] = marker;
      }
      this.$set(this, 'markers', markers);

      // Add a marker for location
      this.add_marker(this.name, this.point.coordinates, 'fa-home', 'green');
      
      // Map fit all points
      map.fitBounds(this.bounds, {
        padding : [10, 10],
      });
    },

    path : function(path){
      // Display path to point
      this.path_layer.clearLayers();
      this.path_layer.addData(path);
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
