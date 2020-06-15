const state = () => ({
  all: [],
  steps: [],
  schedules: [],
});

const getters = {
  programObj(state) {
    return state.all.reduce((obj, item) => ((obj[item.id] = item), obj), {});
  },
  programSchedules(state) {
    return (programId) =>
      state.schedules.filter((s) => s.program_id === programId);
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
  setSchedules(state, schedules) {
    state.schedules = schedules;
  },
  setSteps(state, steps) {
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
