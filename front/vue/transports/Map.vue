<template>
  <div class="map" :style="{height : height + 'px'}"></div>
</template>

<style scoped>
.map {
  border: 1px solid #ccc;
  width: 100%;
  height: 400px;
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
    height : Number,
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
      var server = 'https://{s}.tile.openstreetmap.se/hydda/full/{z}/{x}/{y}.png';
      L.tileLayer(server, {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap <a href="http://openstreetmap.se/" target="_blank">tiles</a> &amp; <a href="http://www.openstreetmap.org/copyright">map data</a>'
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
      // Detect if there are new stops
      var diff = _.differenceWith(stops, this.markers, function(stop, marker){
        return marker != null && stop.id == marker.stop.id;
      });
      if(diff.length == 0)
        return;

      // Display markers for stops
      var map = this.map;
      var that = this;
      var markers = [];

      for(var s in stops){
        // Build marker for each stop
        var stop = stops[s];
        var marker = this.add_marker(stop.name, stop.point.coordinates, 'fa-bus', 'blue');
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
      // Show location & stop
      if(stop === null)
        return;
      var coords_stop = stop.point.coordinates;
      var coords_home = this.point.coordinates;
      this.map.fitBounds([
        [coords_stop[1], coords_stop[0]],
        [coords_home[1], coords_home[0]],
      ], {
        padding : [50, 50],
      });

      // Clean path layer
      this.path_layer.clearLayers();

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
        circle.on('click', function(){
          that.$emit('selected_stop', stop, ls);
        });
        that.stop_circles.addLayer(circle);
      });
    },
  },
}
</script>
