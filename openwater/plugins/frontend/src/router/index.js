import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Dashboard",
    meta: {
      title: "Dashboard",
    },
    component: () =>
      import(/* webpackChunkName: "dashboard-view" */ "../views/Dashboard"),
  },
  {
    path: "/calendar",
    name: "calendar",
    meta: {
      title: "Calendar",
    },
    component: () =>
      import(/* webpackChunkName: "calendar-view" */ "../views/Calendar.vue"),
  },
  {
    path: "/programs",
    component: () =>
      import(
        /* webpackChunkName: "programs-view" */ "../views/program/ProgramsView.vue"
      ),
    children: [
      {
        path: "",
        name: "programs",
        meta: {
          title: "Programs",
        },
        component: () =>
          import(
            /* webpackChunkName: "programs" */ "../views/program/Programs.vue"
          ),
      },
      {
        path: "add",
        name: "add_program",
        meta: {
          title: "Add Program",
          save: true,
        },
        component: () =>
          import(
            /* webpackChunkName: "add-program" */ "../views/program/AddProgram.vue"
          ),
      },
      {
        path: "edit/:id",
        name: "edit_program",
        meta: {
          title: "Edit Program",
          save: true,
        },
        component: () =>
          import(
            /* webpackChunkName: "edit-program" */ "../views/program/EditProgram.vue"
          ),
      },
    ],
  },
  {
    path: "/schedules",
    component: () => import("../views/schedule/SchedulesView.vue"),
    children: [
      {
        path: "",
        name: "programs",
        meta: {
          title: "Schedules",
        },
        component: () =>
          import(
            /* webpackChunkName: "schedules" */ "../views/schedule/Schedules.vue"
          ),
      },
      {
        path: "edit/:id",
        name: "edit_schedule",
        meta: {
          title: "Edit Schedule",
          save: true,
        },
        component: () => import("../views/schedule/EditSchedule"),
      },
      {
        path: "add",
        name: "add_schedule",
        meta: {
          title: "Add Schedule",
          save: true,
        },
        component: () => import("../views/schedule/AddSchedule"),
      },
    ],
  },
  {
    path: "/zones",
    component: () =>
      import(
        /* webpackChunkName: "zones-view" */ "../views/zone/ZonesView.vue"
      ),
    children: [
      {
        path: "",
        name: "zones",
        meta: {
          title: "Zones",
        },
        component: () =>
          import(/* webpackChunkName: "zones" */ "../views/zone/Zones.vue"),
      },
      {
        path: "add",
        name: "add_zone",
        meta: {
          title: "Add Zone",
          save: true,
        },
        component: () =>
          import(
            /* webpackChunkName: "add-zone" */ "../views/zone/AddZone.vue"
          ),
      },
      {
        path: "edit/:id",
        name: "edit_zone",
        meta: {
          title: "Edit Zone",
          save: true,
        },
        component: () =>
          import(
            /* webpackChunkName: "edit-zone" */ "../views/zone/EditZone.vue"
          ),
      },
    ],
  },
  {
    path: "/about",
    name: "about",
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/About.vue"),
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
