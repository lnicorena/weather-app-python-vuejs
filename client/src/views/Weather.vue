<template>
  <div class="app-group">
    <b-container>
      <b-row>
        <b-col>
          <weather-address
            @postalCodeInserted="updateTemperature"
          ></weather-address>
        </b-col>
        <b-col align="center">
          <weather-box ref="box"></weather-box>
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
  methods: {
    updateTemperature(postal_code) {
      this.$refs.box.loadTemperature(postal_code);
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
