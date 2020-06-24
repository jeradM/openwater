<template>
  <fragment>
    <h2 class="headline my-2">Schedules</h2>
    <v-card>
      <v-card-text>
        <SchedulesList :schedules="schedules" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="addSchedule()" color="accent">Add Schedule</v-btn>
      </v-card-actions>
    </v-card>
  </fragment>
</template>

<script>
import SchedulesList from "../schedules/ScheduleList";
export default {
  name: "ProgramSchedules",
  components: { SchedulesList },
  props: {
    schedules: Array,
  },
  methods: {
    addSchedule() {
      this.schedules.push({
        name: "New Schedule",
        schedule_type: "Weekly",
        at: 0,
        enabled: true,
      });
    },
  },
};
</script>

<style scoped>
/*.schedulePanel {*/
/*  border-bottom: 1px solid rgba(0, 0, 0, 0.12);*/
/*}*/
/*.schedulePanel:last-child {*/
/*  border-bottom: none;*/
/*}*/
</style>
