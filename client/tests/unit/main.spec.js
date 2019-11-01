import { shallowMount, createLocalVue } from "@vue/test-utils";
import BootstrapVue from "bootstrap-vue";
import Weather from "@/views/Weather.vue";
import WeatherAddress from "@/components/WeatherAddress.vue";

let localVue = createLocalVue();
localVue.use(BootstrapVue);

describe("Weather.vue", () => {
  it("initialize the component correctly", () => {
    const wrapper = shallowMount(Weather, { localVue });

    let { temperature, location } = wrapper.vm.$data;

    // initial values should be blank
    expect(temperature).toBe("");
    expect(location).toBe("");
  });

  it("set data values", () => {
    const wrapper = shallowMount(Weather, { localVue });

    let values = {
      temperature: "72.3",
      location: "New York, NY"
    };
    wrapper.vm.updateTemperature(values);

    let { temperature, location } = wrapper.vm.$data;

    // assert if data values were updated
    expect(temperature).toBe(values.temperature);
    expect(location).toBe(values.location);
  });

  it("update values from emmited event", () => {
    const wrapper = shallowMount(Weather, { localVue });

    let payload = {
      temperature: "70.5",
      location: "Chicago, IL"
    };
    // child component emmits an event
    wrapper.find(WeatherAddress).vm.$emit("updateTemperatureBox", payload);

    // the event should trigger updateTemperature
    let { temperature, location } = wrapper.vm.$data;

    // here we test parent method was called and updated $data
    expect(temperature).toBe(payload.temperature);
    expect(location).toBe(payload.location);
  });
});
