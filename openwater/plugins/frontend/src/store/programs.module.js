const state = () => ({
  all: [],
  steps: [],
});

const getters = {
  programObj(state) {
    return state.all.reduce((obj, item) => ((obj[item.id] = item), obj), {});
  },
  programSteps(state) {
    return (programId) => state.steps.filter((s) => s.program_id === programId);
  },
  runningProgram(state) {
    return state.all.find((p) => p.is_running) || null;
  },
};

const actions = {};

const mutations = {
  setPrograms(state, programs) {
    state.all = programs;
  },
  setSteps(state, steps) {
    console.log("Set steps: ", steps);
    state.steps = steps;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
