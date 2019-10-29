<template>
  <div id="app">
    <b-navbar type="dark" variant="info">
      <b-container>
        <b-navbar-brand>{{ title }}</b-navbar-brand>
      </b-container>
    </b-navbar>
    <router-view />
  </div>
</template>
<script>
export default {
  data() {
    return {
      title: process.env.VUE_APP_TITLE
    };
  }
};
</script>
