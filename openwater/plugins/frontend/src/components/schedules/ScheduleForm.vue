<template>
  <div>
    <v-row>
      <v-col cols="12" md="4">
        <v-text-field
          v-model.trim="schedule.name"
          label="Name"
          :error-messages="errors.name"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="schedule.program_id"
          :items="programs"
          item-text="name"
          item-value="id"
          label="Program"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="schedule.schedule_type"
          label="Schedule Type"
          :items="scheduleTypes"
          :error-messages="errors.schedule_type"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { SCHEDULE_TYPES } from "../../utils/schedules";

export default {
  name: "ScheduleForm",
  data: () => ({
    scheduleTypes: SCHEDULE_TYPES,
    errors: {},
  }),
  props: {
    schedule: Object,
  },
  computed: {
    programs() {
      return this.$store.state.programs.all;
    },
  },
};
</script>

<style scoped></style>
