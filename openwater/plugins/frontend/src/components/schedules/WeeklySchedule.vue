<template>
  <div>
    <v-row dense>
      <v-col cols="12" sm="6">
        <TimeInput :time="schedule.at" @updated="timeUpdated" label="Time" />
      </v-col>
      <v-col cols="12" sm="6">
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
      <v-col cols="12" sm="2">
        <v-checkbox v-model="repeat" label="Repeat?" />
      </v-col>
      <v-col cols="12" sm="5">
        <v-text-field
          v-model.number="schedule.repeat_every"
          label="Repeat Every (mins)"
          :disabled="!repeat"
        />
      </v-col>
      <v-col cols="12" sm="5">
        <TimeInput
          :time="schedule.repeat_until"
          :disabled="!repeat"
          @updated="repeatUntilUpdated"
          label="Until"
        />
      </v-col>
    </v-row>
    <v-row dense>
      <v-col v-for="dow in days" :key="dow.val">
        {{ dow.short }}
      </v-col>
    </v-row>
    <v-row dense class="justify-space-between">
      <v-col v-for="dow in days" :key="dow.val">
        <v-checkbox
          :input-value="getDow(dow.bit)"
          @change="setDow(dow.bit, $event)"
          :aria-label="dow.long"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { DAYS, DAY_RESTRICTION } from "../../utils/schedules";
import TimeInput from "../TimeInput";

export default {
  name: "WeeklySchedule",
  components: { TimeInput },
  props: {
    schedule: Object,
  },
  data: () => ({
    timeShown: false,
    repeat_: false,
  }),
  methods: {
    getDow(val) {
      return !!(this.schedule.dow_mask & (1 << val));
    },
    setDow(val, checked) {
      if (checked) this.schedule.dow_mask |= 1 << val;
      else this.schedule.dow_mask &= ~(1 << val);
    },
    timeUpdated(val) {
      this.schedule.at = val;
    },
    repeatUntilUpdated(val) {
      this.schedule.repeat_until = val;
    },
  },
  computed: {
    days() {
      return DAYS;
    },
    dayRestriction() {
      return DAY_RESTRICTION;
    },
    repeat: {
      get() {
        return this.repeat_;
      },
      set(val) {
        if (!val) {
          this.schedule.repeat_every = null;
          this.schedule.repeat_until = null;
        }
        this.repeat_ = val;
      },
    },
  },
  mounted() {
    this.repeat_ = !!this.schedule.repeat_every;
  },
};
</script>

<style scoped></style>
