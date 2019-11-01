import { shallowMount, createLocalVue } from "@vue/test-utils";
import BootstrapVue from "bootstrap-vue";
import WeatherAddress from "@/components/WeatherAddress.vue";
import axios from "axios";
const MockAdapter = require("axios-mock-adapter");
const mock = new MockAdapter(axios);

let localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.prototype.$axios = axios;

describe("WeatherAddress.vue", () => {
  afterAll(() => {
    mock.restore();
  });
  beforeEach(() => {
    mock.reset();
  });

  it("initialize the component correctly", () => {
    const wrapper = shallowMount(WeatherAddress, { localVue });
    let { gkey, address, suggestions, errorMessage } = wrapper.vm.$data;
    expect(gkey).toBe(gkey);
    expect(address).toBe("");
    expect(suggestions).toStrictEqual([]);
    expect(errorMessage).toBe("");
  });

  it("load search history", async () => {
    mock.onGet("http://localhost:8081/search?q=").reply(200, {
      data: {
        status: "OK",
        result: ["Address 1", "Address 2"]
      }
    });
    const wrapper = shallowMount(WeatherAddress, { localVue });
    await wrapper.vm.getSuggestions();

    // should have no errors after a successful request
    expect(wrapper.vm.$data.errorMessage).toBe("");
  });
});
