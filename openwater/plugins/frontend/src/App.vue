<template>
  <v-app>
    <Websocket />
    <v-app-bar app clipped dark color="primary">
      <v-app-bar-nav-icon @click="drawer = !drawer" class="d-lg-none" />
      <v-toolbar-title>{{ routeName }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="canSave" @click="saveFunc" text>Save</v-btn>
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
      :mini-variant="!mobile && !menuOpen"
      :temporary="mobile"
      :permanent="!mobile"
      fixed
      app
    >
      <v-list-item>
        <v-list-item-icon v-on:click="menuOpen = !menuOpen">
          <v-icon class="d-none d-lg-flex">{{
            menuOpen ? "mdi-menu-open" : "mdi-menu"
          }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            OpenWater
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-divider />
      <v-list dense nav class="py-0">
        <v-list-item
          v-for="item in views"
          :key="item.title"
          link
          :to="item.to"
          color="primary"
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-content app>
      <v-sheet class="pa-6">
        <router-view></router-view>
      </v-sheet>
    </v-content>
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.type"
      :timeout="snackbar.timeout"
      bottom
      left
    >
      {{ snackbar.msg }}
      <template v-slot:action>
        <v-btn text @click="snackbar.show = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import Websocket from "./components/Websocket";
import { EventBus } from "./utils/event-bus";

export default {
  name: "App",
  components: {
    Websocket,
  },
  data: () => ({
    menuOpen: true,
    drawer: false,
    snackbar: {
      show: false,
      msg: "",
      type: "info",
      timeout: 5000,
    },
    views: [
      { title: "Dashboard", icon: "mdi-view-dashboard", to: "/" },
      { title: "Calendar", icon: "mdi-calendar-month", to: "/calendar" },
      { title: "Zones", icon: "mdi-sprinkler-variant", to: "/zones" },
      {
        title: "Programs",
        icon: "mdi-clipboard-list-outline",
        to: "/programs",
      },
      { title: "Schedules", icon: "mdi-calendar-clock", to: "/schedules" },
      { title: "Plugins", icon: "mdi-toy-brick", to: "/plugins" },
    ],
  }),
  computed: {
    mobile() {
      return this.$vuetify.breakpoint.mdAndDown;
    },
    routeName() {
      return this.$route.meta.title;
    },
    canSave() {
      return this.$route.meta.save;
    },
    saveFunc() {
      return this.canSave && this.$store.state.saveFunc
        ? this.$store.state.saveFunc
        : () => {};
    },
  },
  watch: {
    mobile(val) {
      this.drawer = !val;
    },
  },
  created() {
    EventBus.$on("snackbar", ({ msg, type = "info", timeout = 5000 }) => {
      this.snackbar = {
        show: true,
        msg,
        type,
        timeout,
      };
    });
  },
};
</script>
