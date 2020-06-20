<template>
  <v-sheet>
    <v-btn
      to="/programs/add"
      color="secondary"
      fab
      absolute
      bottom
      right
      class="mb-12 mr-2"
    >
      <v-icon>mdi-plus</v-icon>
    </v-btn>
    <SchedulesList />
  </v-sheet>
</template>

<script>
import SchedulesList from "../../components/schedules/ScheduleList";

export default {
  name: "Schedules",
  components: { SchedulesList },
};
</script>

<style scoped></style>
