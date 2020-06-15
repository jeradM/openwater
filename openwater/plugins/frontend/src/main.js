import Vue from "vue";
import Vuex from "vuex";
import App from "./App.vue";
import router from "./router";
import vuetify from "./plugins/vuetify";
import VueFilterDateFormat from "@vuejs-community/vue-filter-date-format";
import { Plugin } from "vue-fragment";

import store from "./store";

Vue.config.productionTip = false;
Vue.use(VueFilterDateFormat);
Vue.use(Vuex);
Vue.use(Plugin);

new Vue({
  router,
  vuetify,
  store,
  render: (h) => h(App),
}).$mount("#app");
