module.exports = {
  props : {
    widgetId : String,
  },
  computed : {
    widget : function(){
      return this.$store.state.widgets[this.widgetId];
    },
  },
};
