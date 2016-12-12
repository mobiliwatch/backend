<template>
  <article class="tile is-child box" v-if="widget">
    <div class="content">

      <Note v-if="widget.type == 'NoteWidget'" :widgetId="widget.id" />
      <Weather v-if="widget.type == 'WeatherWidget'" :widgetId="widget.id" />
      <Clock v-if="widget.type == 'ClockWidget'" :widgetId="widget.id" />
      <LocationWidget v-if="widget.type == 'LocationWidget'" :widgetId="widget.id" />
      <Disruption v-if="widget.type == 'DisruptionWidget'" :widgetId="widget.id" />

    </div>
  </article>
</template>

<script>
var mixins = require('./widgets/mixins.js');
var Note = require('./widgets/Note.vue');
var Weather = require('./widgets/Weather.vue');
var Clock = require('./widgets/Clock.vue');
var LocationWidget = require('./widgets/Location.vue');
var Disruption = require('./widgets/Disruption.vue');

module.exports = {
  mixins : [mixins, ],
  components : {
    Note : Note,
    Weather : Weather,
    Clock : Clock,
    LocationWidget : LocationWidget, // reserved word location
    Disruption : Disruption,
  },
  data : function(){
    return {};
  },
};
</script>
