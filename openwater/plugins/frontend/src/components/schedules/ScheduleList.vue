<template>
  <v-list>
    <SchedulesListItem
      v-for="schedule in schedules"
      :schedule="schedule"
      :key="schedule.id"
    />
  </v-list>
</template>

<script>
import SchedulesListItem from "./SchedulesListItem";

export default {
  name: "SchedulesList",
  components: { SchedulesListItem },
  props: {
    schedules: Array,
  },
};
</script>

<style scoped></style>
