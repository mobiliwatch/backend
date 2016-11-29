var _ = require('lodash');

module.exports = {
  props : {
    widgetId : String,
  },
  data : function(){
    return {
      saving : false,
    };
  },
  computed : {
    widget : function(){
      return this.$store.state.widgets[this.widgetId];
    },
  },
  methods: {
    save : function(extra_data){
      var data = {
        id : this.widget.id,
      };
      if(extra_data)
        data = _.merge(data, extra_data);

      this.$set(this, 'saving', true);
      var that = this;
      this.$store.dispatch('update_widget', data)
      .then(function(){
        that.$set(that, 'saving', false);
      })
      .catch(function(){
        that.$set(that, 'saving', false);
      });
    },
  },
};
