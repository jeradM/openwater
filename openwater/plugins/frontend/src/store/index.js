import Vue from "vue";
import Vuex from "vuex";
import zones from "./zones.module";
import programs from "./programs.module";
import schedules from "./schedules.module";

Vue.use(Vuex);

const debug = process.env.NODE_ENV !== "production";

export default new Vuex.Store({
  modules: {
    programs,
    schedules,
    zones,
  },
  state() {
    return {
      saveFunc: null,
      canSave: false,
      scheduleTypes: ["Weekly", "Interval", "Single"],
    };
  },
  mutations: {
    setSaveFunc(state, f) {
      state.saveFunc = f;
    },
  },
  strict: debug,
});
