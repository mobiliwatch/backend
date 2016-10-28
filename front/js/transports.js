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

      L.tileLayer('http://{s}.grayscale.osm.maptiles.xyz/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
          '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
          'Imagery © <a href="http://mapbox.com">Mapbox</a>',
        id: 'mapbox.light'
      }).addTo(map);
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
