import { shallowMount, createLocalVue } from "@vue/test-utils";
import BootstrapVue from "bootstrap-vue";
import WeatherBox from "@/components/WeatherBox.vue";

let localVue = createLocalVue();
localVue.use(BootstrapVue);

describe("WeatherBox.vue", () => {
  it("initialize the component correctly", () => {
    const wrapper = shallowMount(WeatherBox, {
      propsData: {
        temperature: "",
        location: ""
      },
      localVue
    });

    expect(wrapper.vm.temp).toBe("-");
    expect(wrapper.vm.loc).toBe("-");
  });

  it("seting WeatherBox properties", () => {
    let location_name = "New York, NY";
    const wrapper = shallowMount(WeatherBox, {
      propsData: {
        temperature: "73.6",
        location: location_name
      },
      localVue
    });

    // displayed temperature should be rounded to 74
    expect(wrapper.vm.temp).toBe(74);

    // displayed location name should be the same
    expect(wrapper.vm.loc).toBe(location_name);
  });
});
