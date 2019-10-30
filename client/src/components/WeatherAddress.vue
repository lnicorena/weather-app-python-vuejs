<template>
  <div>
    <b-form-group>
      <vue-bootstrap-typeahead
        placeholder="Enter an address"
        v-model="address"
        :data="suggestions"
        :minMatchingChars="0"
        @hit="getLocation()"
        @keyup.enter.native="getLocation()"
      />
      <label class="text-danger small">{{ errorMessage }}</label>
    </b-form-group>
    <b-button @click="getLocation()" block variant="success"
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
    getLocation() {
      this.$axios
        .get(
          process.env.VUE_APP_API_URL +
            `/temperature?address=${this.encoded_address}`
        )
        .then(data => {
          console.log("then", data);
          if (data.data.status == "OK") {
            this.$emit("updateTemperatureBox", data.data.result);
            this.errorMessage = "";
          } else {
            this.errorMessage = this.formatErrors(data.data.errors);
          }
        })
        .catch(error => {
          if (error.response && error.response.data.errors) {
            this.errorMessage = this.formatErrors(error.response.data.errors);
          } else {
            this.errorMessage = this.formatErrors(error.message);
          }
        });
    },

    getSuggestions() {
      this.$axios
        .get(process.env.VUE_APP_API_URL + `/search?q=${this.address}`)
        .then(data => {
          if (data.data.status == "OK") {
            this.suggestions = data.data.result;
          } else {
            this.errorMessage = this.formatErrors(data.data.errors);
          }
        })
        .catch(error => {
          console.log("error", error);
          if (error.response && error.response.data.errors) {
            this.errorMessage = this.formatErrors(error.response.data.errors);
          }
        });
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
