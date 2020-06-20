<template>
  <v-expansion-panel>
    <v-expansion-panel-header>
      <template v-slot:default>
        <v-row>
          <v-col cols="1" class="pa-1 d-flex">
            <v-icon>mdi-calendar-clock</v-icon>
          </v-col>
          <v-col cols="11" class="pa-1">
            <v-row>
              <span class="subtitle-1">{{ title }}</span>
            </v-row>
          </v-col>
        </v-row>
      </template>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn :to="editUrl" color="primary" text>Edit</v-btn>
      </v-card-actions>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import { getScheduleTitle } from "../../utils/schedules";

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
  },
};
</script>

<style scoped></style>
