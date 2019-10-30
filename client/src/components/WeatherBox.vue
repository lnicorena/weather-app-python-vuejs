<template>
  <b-card
    bg-variant="info"
    text-variant="white"
    :header="place"
    class="text-center"
    style="max-width: 18rem;"
  >
    <b-card-text class="display-4">{{ temp }} &deg;F</b-card-text>
  </b-card>
</template>

<script>
export default {
  name: "WeatherBox",
  data() {
    return {
      temp: "-",
      place: "New York City, NY",
      wkey: process.env.VUE_APP_OPENWEATHER_API_KEY,
      zip: ""
    };
  },

  methods: {
    loadTemperature(postal_code) {
      this.zip = postal_code;
      let apiCall = `http://api.openweathermap.org/data/2.5/weather?zip=${this.zip}&units=imperial&APPID=${this.wkey}`;
      this.$axios.get(apiCall).then(data => {
        this.weatherCallback(data.data);
      });
    },
    weatherCallback(weatherData) {
      this.place = weatherData.name;
      this.temp = weatherData.main.temp;
    }
  }
};
</script>
