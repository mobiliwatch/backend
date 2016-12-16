var _ = require('lodash');

module.exports = {
  props : {
    widgetId : String,
    groupId : Number,
  },
  data : function(){
    return {
      saving : false,
      deleting: false,
      error : null,
    };
  },
  computed : {
    widget : function(){
      return this.$store.state.widgets[this.widgetId];
    },
  },
  methods: {
    save : function(extra_data){
      this.$set(this, 'error', null);
      var data = {
        id : this.widget.id,
      };
      if(extra_data)
        data = _.merge(data, extra_data);

      this.$set(this, 'saving', true);
      var that = this;
      return this.$store.dispatch('update_widget', data)
      .then(function(){
        that.$set(that, 'saving', false);
      })
      .catch(function(error){
        that.$set(that, 'saving', false);
        that.$set(that, 'error', error);
      });
    },
    delete_widget : function(){
      this.$set(this, 'error', null);
      var data = {
        id : this.widget.id,
      };

      this.$set(this, 'deleting', true);
      var that = this;
      return this.$store.dispatch('delete_widget', data)
      .then(function(){
        that.$set(that, 'deleting', false);
      })
      .catch(function(){
        that.$set(that, 'deleting', false);
      });
    },
  },
};
