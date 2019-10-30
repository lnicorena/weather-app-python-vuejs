<template>
  <b-card
    bg-variant="info"
    text-variant="white"
    :header="loc"
    class="text-center"
    style="max-width: 18rem;"
  >
    <b-card-text class="display-4">{{ temp }} &deg;F</b-card-text>
  </b-card>
</template>

<script>
export default {
  name: "WeatherBox",
  props: {
    temperature: {
      type: [String, Number],
      required: true
    },
    location: {
      type: String,
      required: true
    }
  },
  computed: {
    temp: function() {
      return this.temperature ? Math.round(parseFloat(this.temperature)) : "-";
    },
    loc: function() {
      return this.location ? this.location : "-";
    }
  }
};
</script>
