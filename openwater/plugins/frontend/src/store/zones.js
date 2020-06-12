const state = () => ({
  all: [],
  types: {
    GPIO: {
      id: "GPIO",
      attrs: [{ id: "pin", type: "number", label: "GPIO Output Pin" }],
    },
    SHIFT_REGISTER: {
      id: "SHIFT_REGISTER",
      attrs: [
        {
          id: "sr_idx",
          type: "select",
          label: "Shift Register Pin",
          options: [0, 1, 2, 3, 4, 5, 6, 7],
        },
      ],
    },
  },
  soilTypes: [
    { id: "SAND", name: "Sand" },
    { id: "SANDY_LOAM", name: "Sandy Loam" },
    { id: "LOAM", name: "Loam" },
    { id: "CLAY", name: "Clay" },
  ],
});

const getters = {
  zoneObj(state) {
    return state.all.reduce((obj, item) => ((obj[item.id] = item), obj), {});
  },
  zoneTypes(state) {
    return state.types;
  },
  zoneTypeList(state) {
    return Object.keys(state.types);
  },
  soilTypes(state) {
    return state.soilTypes;
  },
};

const actions = {
  // fetchZones({ commit }) {
  //   fetch("http://localhost:8000/api/zones")
  //     .then((res) => res.json())
  //     .then((data) => commit("setZones", data));
  // },
};

const mutations = {
  setZones(state, zones) {
    state.all = zones;
  },
  setTypes(state, types) {
    state.types = types;
  },
  setSoilTypes(state, soilTypes) {
    state.soilTypes = soilTypes;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
