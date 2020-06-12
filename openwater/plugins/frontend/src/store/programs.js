const state = () => ({
  all: [],
});

const getters = {
  programObj(state) {
    return state.all.reduce((obj, item) => ((obj[item.id] = item), obj), {});
  },
  schedules(state) {
    return state.all.map((p) => p.schedules).flat();
  },
  runningProgram(state) {
    return state.all.find((p) => p.is_running) || null;
  },
};

const actions = {
  //   fetchZones({ commit }) {
  //     fetch("http://localhost:8000/api/zones")
  //       .then((res) => res.json())
  //       .then((data) => commit("setZones", data));
  //   },
};

const mutations = {
  setPrograms(state, programs) {
    state.all = programs;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
