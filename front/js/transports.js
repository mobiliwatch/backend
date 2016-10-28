Vue.component('transports-map', {
  template: '<div id="transports-map" class="map"></div>'
});

var transports = function(element_id, lng, lat){
  var app = new Vue({
    el: element_id,
    data: {
      message: 'Hello Vue!'
    }
  })
};
