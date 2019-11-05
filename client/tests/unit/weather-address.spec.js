import { shallowMount, createLocalVue } from "@vue/test-utils";
import BootstrapVue from "bootstrap-vue";
import WeatherAddress from "@/components/WeatherAddress.vue";
import axios from "axios";

let localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.prototype.$axios = axios;

describe("WeatherAddress.vue", () => {
  it("initialize the component correctly", () => {
    const wrapper = shallowMount(WeatherAddress, { localVue });
    let { gkey, address, suggestions, errorMessage } = wrapper.vm.$data;
    expect(gkey).toBe(gkey);
    expect(address).toBe("");
    expect(suggestions).toStrictEqual([]);
    expect(errorMessage).toBe("");
  });

  /*
  it("load search history", async () => {
    let { data } = await axios.get("http://localhost:8081/search?q=");
    const wrapper = shallowMount(WeatherAddress, { localVue });
    await wrapper.vm.getSuggestions();

    // should have no errors after a successful request
    expect(wrapper.vm.$data.errorMessage).toBe("");
    expect(wrapper.vm.$data.suggestions).toStrictEqual(data.result);
  });

  
  it("get temperature", async (done) => {
    let address = "515 N. State Street, Chicago";

    // Load some address temperature
    let { data } = await axios.get(
      `http://localhost:8081/temperature?address=${address}`
    );

    const wrapper = shallowMount(WeatherAddress, { localVue });

    // set address field
    wrapper.vm.$data.address = address;

    await wrapper.vm.getTemperature();

    wrapper.vm.$nextTick(() => {

      // should have no errors after a successful request
      expect(wrapper.emitted().temperature).toBeTruthy();
      expect(wrapper.emitted().location).toBeTruthy();
      done()
    });
  });
  */
});
