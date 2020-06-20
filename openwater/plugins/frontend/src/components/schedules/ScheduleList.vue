<template>
  <v-sheet max-width="800" class="mx-auto">
    <v-expansion-panels>
      <template v-for="schedule in schedules">
        <SchedulesListItem :schedule="schedule" :key="schedule.id" />
      </template>
    </v-expansion-panels>
  </v-sheet>
</template>

<script>
import SchedulesListItem from "./SchedulesListItem";

export default {
  name: "SchedulesList",
  components: { SchedulesListItem },
  computed: {
    schedules() {
      return this.$store.state.programs.schedules;
    },
  },
};
</script>

<style scoped></style>
