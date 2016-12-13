<script>
//
// Toggle button with slider
//
// Usage:
//    <toggle-button
//      option1="your first label "
//    [ option2="your second label" ]
//      v-model="yourVariable">
//    </toggle-button>
//
// The option2 attribute is optionnal:
// - if provided, the value emitted through yourVariable is equal
//     either to the content of option1 or to the content of option2
// - if not provided, the value emitted through yourVariable is binary:
//     false when slider is in left position,
//     true when slider is in right position
//
// The provided variable must be initialized (to either option1/option2
// or boolean is option2 is not provided), so the slider can be initialized
// also in the correct position
//

// Some hints found on http://www.w3schools.com/howto/howto_css_switch.asp
module.exports = {
  props: {
    'option1': String,
    'option2': String,
    'value': String | Boolean
  },
  data: function () {
    return {
      randomId: 'input-' + Math.random(),
      state: undefined
    }
  },
  computed: {
    // when option2 is not provided, the toggleButton becomes binary
    isBinary: function() {
      return this.option2 == false
    }
  },
  // initialize internal state from the value of the provided variable
  created: function () {
    this.updateState(this.value)
  },
  methods: {
    // update internal state:
    // - if binary, state = checked
    // - else, state = option1 when not checked (slider on the left),
    //         state = option2 when checked (slider on the right)
    updateState: function (checked) {
      this.state = this.isBinary ? checked : (checked ? this.option2 : this.option1)
    },
    // when checkbox state changes, update the internal state and emit it to the parent
    onChange: function (event) {
      this.updateState(event.target.checked)
      this.$emit('input', this.state)
    },
    // initialize the checked attribute from the value of the provided variable
    checked: function(value) {
      return this.isBinary ? value : value == this.option2
    }
  }
}
</script>

<template>
  <div class="toggleContainer">
    <div>{{ option1 }}</div>
    <label v-bind:for="randomId" class="toggleBox">
      <input type="checkbox"
        v-bind:id="randomId"
        v-bind:checked="checked(value)"
        v-on:change="onChange">
      <div class="slider round"></div>
    </label>
    <div>{{ option2 }}</div>
  </div>
</template>

<style>
  /* box around labels and button */
  .toggleContainer {
    display: flex;
  }

  .toggleContainer div {
    margin: auto 0px;
  }

  /* box around the slider */
  .toggleBox {
    position: relative;
    display: inline-block;
    width: 60px;
    height: 34px;
    margin: auto 10px;
  }

  /* hide default HTML checkbox */
  .toggleBox input {
    display: none;
  }

  /* slider */
  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    -webkit-transition: .4s;
    transition: .4s;
  }

  .slider:before {
    position: absolute;
    content: "";
    height: 26px;
    width: 26px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    -webkit-transition: .4s;
    transition: .4s;
  }

  input:checked + .slider {
    background-color: #2196F3;
  }

  input:focus + .slider {
    box-shadow: 0 0 1px #2196F3;
  }

  input:checked + .slider:before {
    -webkit-transform: translateX(26px);
    -ms-transform: translateX(26px);
    transform: translateX(26px);
  }

  /* rounded slider */
  .slider.round {
    border-radius: 34px;
  }

  .slider.round:before {
    border-radius: 50%;
  }
</style>
