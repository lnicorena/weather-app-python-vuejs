<template>
  <b-card
    bg-variant="info"
    text-variant="white"
    :header="place"
    class="text-center"
    style="max-width: 18rem;"
  >
    <b-card-text class="display-4">{{ degrees }} &deg;F</b-card-text>
  </b-card>
</template>

<script>
export default {
  name: "WeatherBox",
  data() {
    return {
      degrees: "-",
      place: "New York City, NY"
    };
  }
};
</script>
