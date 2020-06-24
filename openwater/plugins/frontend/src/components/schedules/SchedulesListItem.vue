<template>
  <v-list-item :to="editUrl" link>
    <v-list-item-icon>
      <v-icon>{{ icon }}</v-icon>
    </v-list-item-icon>
    <v-list-item-content>
      <v-list-item-title>{{ title }}</v-list-item-title>
      <v-list-item-subtitle>{{ subtitle }}</v-list-item-subtitle>
    </v-list-item-content>
  </v-list-item>
</template>

<script>
import { getScheduleSubtitle, getScheduleTitle } from "../../utils/schedules";

export default {
  name: "SchedulesListItem",
  props: {
    schedule: Object,
  },
  computed: {
    editUrl() {
      return `/schedules/edit/${this.schedule.id}`;
    },
    title() {
      return getScheduleTitle(this.schedule);
    },
    subtitle() {
      return getScheduleSubtitle(this.schedule);
    },
    icon() {
      switch (this.schedule.schedule_type) {
        case "Weekly":
          return "mdi-calendar-range";
        case "Interval":
          return "mdi-calendar-multiselect";
        default:
          return "mdi-calendar-today";
      }
    },
  },
};
</script>

<style scoped></style>
