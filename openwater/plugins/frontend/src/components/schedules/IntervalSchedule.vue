<template>
  <div>
    <v-row dense>
      <v-col cols="12" md="4">
        <DateInput
          label="Start Day"
          :date="schedule.start_day"
          @changed="dateUpdated"
        />
      </v-col>
      <v-col cols="12" md="4">
        <TimeInput :time="schedule.at" @updated="timeUpdated" label="At time" />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="schedule.days_restriction"
          :items="dayRestriction"
          label="Day Restriction"
          item-text="label"
          item-value="val"
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field
          v-model.number="schedule.day_interval"
          @keydown="dayIntervalChange"
          label="Day Interval"
        />
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field
          v-model.number="schedule.minute_interval"
          @keydown="minIntervalChange"
          label="Minute Interval"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { DAY_RESTRICTION } from "../../utils/schedules";
import TimeInput from "../TimeInput";
import DateInput from "../DateInput";

export default {
  name: "IntervalSchedule",
  components: { DateInput, TimeInput },
  props: {
    schedule: Object,
  },
  methods: {
    timeUpdated(val) {
      this.schedule.at = val;
    },
    dateUpdated(val) {
      this.schedule.start_day = val;
    },
    dayIntervalChange() {
      this.schedule.minute_interval = null;
    },
    minIntervalChange() {
      this.schedule.day_interval = null;
    },
  },
  computed: {
    dayRestriction() {
      return DAY_RESTRICTION;
    },
  },
};
</script>

<style scoped></style>
