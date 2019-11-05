<template>
  <div class="address-search-group">
    <b-form-group>
      <vue-bootstrap-typeahead
        placeholder="Enter an address"
        v-model="address"
        :data="suggestions"
        :minMatchingChars="0"
        @hit="getTemperature()"
        @keyup.enter.native="getTemperature()"
      />
      <label class="text-danger small">{{ errorMessage }}</label>
    </b-form-group>
    <b-button @click="getTemperature()" block variant="success"
      >show me the current temperature</b-button
    >
  </div>
</template>

<script>
import * as _ from "lodash";
import VueBootstrapTypeahead from "vue-bootstrap-typeahead";

export default {
  name: "WeatherAddress",
  components: { VueBootstrapTypeahead },
  data() {
    return {
      gkey: process.env.GOOGLE_API_KEY,
      address: "",
      suggestions: [],
      errorMessage: ""
    };
  },
  computed: {
    encoded_address() {
      return encodeURI(this.address);
    }
  },
  created() {
    this.debouncedQuery = _.debounce(this.getSuggestions, 500);
  },
  mounted() {
    this.getSuggestions();
  },
  watch: {
    address: function() {
      // Get the text from the input when user stops typing
      this.debouncedQuery();
    }
  },
  methods: {
    async getTemperature() {
      try {
        const { data } = await this.$axios.get(
          `${process.env.VUE_APP_API_URL}/temperature?address=${this.encoded_address}`
        );
        if (data.status != "OK")
          throw new Error("semething went wrong with the temperature call");

        this.$emit("updateTemperatureBox", data.result);
        this.errorMessage = "";
      } catch (e) {
        this.errorHandler(e);
        window.console.error("Failure!", e);
      }
    },
    async getSuggestions() {
      try {
        const { data } = await this.$axios.get(
          `${process.env.VUE_APP_API_URL}/search?q=${this.address}`
        );
        if (data.status != "OK")
          throw new Error("semething went wrong with the search call");

        this.suggestions = data.result;
      } catch (e) {
        this.errorHandler(e);
        window.console.error("Failure!", e);
      }
    },
    // getLocation() {
    //   this.$axios
    //     .get(
    //       process.env.VUE_APP_API_URL +
    //         `/temperature?address=${this.encoded_address}`
    //     )
    //     .then(data => {
    //       if (data.data.status == "OK") {
    //         this.$emit("updateTemperatureBox", data.data.result);
    //         this.errorMessage = "";
    //       } else {
    //         console.log("semething went wrong", data);
    //       }
    //     })
    //     .catch(this.errorHandler);
    // },
    // getSuggestions() {
    //   this.$axios
    //     .get(process.env.VUE_APP_API_URL + `/search?q=${this.address}`)
    //     .then(data => {
    //       if (data.data.status == "OK") {
    //         this.suggestions = data.data.result;
    //       }
    //     })
    //     .catch(this.errorHandler);
    // },

    errorHandler(error) {
      if (error.response && error.response.data && error.response.data.errors) {
        this.errorMessage = this.formatErrors(error.response.data.errors);
      } else {
        this.errorMessage = this.formatErrors(error.message);
      }
    },

    formatErrors(errors) {
      return (
        "Some error occuried in the request. Details:\n" +
        (typeof errors == Array ? errors.join(";\n") : errors)
      );
    }
  }
};
</script>
