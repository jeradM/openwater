import Vue from "vue";
import Vuex from "vuex";
import zones from "./zones";
import programs from "./programs";

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== "production";

export default new Vuex.Store({
  modules: {
    zones,
    programs,
  },
  state() {
    return {
      saveFunc: null,
      canSave: false,
    };
  },
  mutations: {
    setSaveFunc(state, f) {
      state.saveFunc = f;
    },
  },
  strict: debug,
});
