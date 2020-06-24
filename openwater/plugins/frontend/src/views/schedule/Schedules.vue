<template>
  <v-sheet>
    <v-btn
      to="/schedules/add"
      color="secondary"
      fab
      fixed
      bottom
      right
      class="mr-2"
    >
      <v-icon>mdi-plus</v-icon>
    </v-btn>
    <v-sheet max-width="800" class="mx-auto">
      <v-card>
        <SchedulesList :schedules="schedules" />
      </v-card>
    </v-sheet>
  </v-sheet>
</template>

<script>
import SchedulesList from "../../components/schedules/ScheduleList";

export default {
  name: "Schedules",
  components: { SchedulesList },
  computed: {
    schedules() {
      return this.$store.state.schedules.all;
    },
  },
};
</script>

<style scoped></style>
