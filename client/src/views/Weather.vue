<template>
  <div class="app-group">
    <b-container>
      <b-row>
        <b-col>
          <weather-address
            @updateTemperatureBox="updateTemperature"
          ></weather-address>
        </b-col>
        <b-col align="center">
          <weather-box
            ref="box"
            :temperature="temperature"
            :location="location"
          ></weather-box>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import WeatherAddress from "@/components/WeatherAddress.vue";
import WeatherBox from "@/components/WeatherBox.vue";

export default {
  name: "Weather",
  components: {
    WeatherAddress,
    WeatherBox
  },
  data() {
    return {
      temperature: "",
      location: ""
    };
  },
  methods: {
    updateTemperature(payload) {
      this.temperature = payload.temperature;
      this.location = payload.location;
    }
  }
};
</script>

<style scoped>
.app-group {
  padding: 1.5rem;
  margin-top: 1.5rem;
}
</style>
