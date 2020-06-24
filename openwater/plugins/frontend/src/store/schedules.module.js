const state = () => ({
  all: [],
});

const getters = {
  schedulesObj(state) {
    return state.all.reduce((obj, item) => ((obj[item.id] = item), obj), {});
  },
  forProgram: (state) => (programId) => {
    console.log("programId: ", programId);
    return state.all.filter((schedule) => schedule.program_id === programId);
  },
};

const actions = {
  async saveSchedule(context, { schedule }) {
    let url = `http://${location.host}/api/schedules`;
    if (schedule.id) url += `/${schedule.id}`;
    const method = schedule.id ? "put" : "post";
    return await fetch(url, {
      method: method,
      header: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(schedule),
    });
  },
};

const mutations = {
  setSchedules(state, schedules) {
    state.all = schedules;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
