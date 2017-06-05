<template>
  <div id="trip">
    Trip !
    <pre>
      {{ trip }}
    </pre>
  </div>
</template>

<script>
module.exports = {
  props : {
    id: Number,
  },
  mounted : function(){
    console.info('Loading trip', this.id);
    // Load trip details
    var url = '/api/trip/' + this.id+ '/';
    this.$http.get(url).then(function(resp){
      this.$store.commit('use_trip', resp.body);
    });
  },
  computed : {
    trip : function(){
      return this.$store.state.trip;
    },
  }
};
</script>
