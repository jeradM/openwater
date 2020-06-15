<template>
  <fragment>
    <h2 class="headline my-2">Schedules</h2>
    <v-card>
      <v-card-text>
        <v-expansion-panels class="flex-column" flat>
          <ProgramSchedule
            class="schedulePanel"
            v-for="(schedule, idx) in schedules"
            :key="idx"
            :schedule="schedule"
            :idx="idx"
          />
        </v-expansion-panels>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="accent">Add Schedule</v-btn>
      </v-card-actions>
    </v-card>
  </fragment>
</template>

<script>
import ProgramSchedule from "./ProgramSchedule";
export default {
  name: "ProgramSchedules",
  components: { ProgramSchedule },
  props: {
    schedules: Array,
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
