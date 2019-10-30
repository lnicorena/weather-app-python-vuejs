<template>
  <div>
    <b-form-group>
      <vue-bootstrap-typeahead
        placeholder="Enter an address"
        v-model="address"
        :data="suggestions"
        :minMatchingChars="0"
      />
    </b-form-group>
    {{ address }}
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
      gkey: process.env.VUE_APP_GOOGLE_API_KEY,
      address: "",
      suggestions: ["Canada", "USA", "Mexico"],
      postal_code: "",
      msg: "."
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
  watch: {
    address: function(neww, old) {
      console.log(neww, old);
      this.debouncedQuery();
    }
  },
  methods: {
    getLocation() {
      let url = `https://maps.googleapis.com/maps/api/geocode/json?key=${this.gkey}&address=${this.encoded_address}&sensor=false"`;

      this.$axios.get(url).then(data => {
        console.log(data);
        this.postal_code = this.getPostalCode(data.data);
        if (this.postal_code != "") {
          this.$emit("postalCodeInserted", this.postal_code);
        }
      });
    },
    getPostalCode(json) {
      console.log("result", json);
      // Sem resultados
      if (json["results"].length == 0) {
        return "";
      }
      let ad = json["results"][0]["address_components"];
      for (let key in ad) {
        if (ad[key]["types"].indexOf("postal_code") != -1) {
          return ad[key]["long_name"];
        }
      }

      // endereco incompleto
      return "";
    },

    getSuggestions() {
      console.log(this.address);
      this.suggestions = [this.address];
    }
  }
};
</script>
