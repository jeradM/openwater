<template>
  <div>
    <v-row dense>
      <v-col cols="12" sm="6">
        <v-menu
          ref="showTime"
          v-model="timeShown"
          :close-on-content-click="false"
          return-value.sync="time"
          offset-y
        >
          <template v-slot:activator="{ attrs, on }">
            <v-text-field
              v-model="time"
              label="Time"
              readonly
              v-bind="attrs"
              v-on="on"
            />
          </template>
          <v-time-picker
            v-model="time"
            full-width
            @click:minute="$refs.showTime.save(time)"
          />
        </v-menu>
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
    <v-row dense>
      <v-col v-for="dow in days" :key="dow.label">
        {{ dow.label }}
      </v-col>
    </v-row>
    <v-row dense>
      <v-col v-for="dow in days" :key="dow.label">
        <v-checkbox
          :input-value="getDow(dow.val)"
          @change="setDow(dow.val, $event)"
          :aria-label="dow.name"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
const DAY_RESTRICTION = [
  { label: "None", val: "" },
  { label: "Even", val: "E" },
  { label: "Odd", val: "O" },
];
const DAYS = [
  { name: "Sunday", label: "Sun", val: 0 },
  { name: "Monday", label: "Mon", val: 1 },
  { name: "Tuesday", label: "Tue", val: 2 },
  { name: "Wednesday", label: "Wed", val: 3 },
  { name: "Thursday", label: "Thu", val: 4 },
  { name: "Friday", label: "Fri", val: 5 },
  { name: "Saturday", label: "Sat", val: 6 },
];

export default {
  name: "WeeklySchedule",
  props: {
    schedule: Object,
  },
  data: () => ({
    days: DAYS,
    dayRestriction: DAY_RESTRICTION,
    timeShown: false,
  }),
  methods: {
    getDow(val) {
      return !!(this.schedule.dow_mask & (1 << val));
    },
    setDow(val, checked) {
      if (checked) this.schedule.dow_mask |= 1 << val;
      else this.schedule.dow_mask &= ~(1 << val);
    },
  },
  computed: {
    time: {
      get() {
        return `${Math.floor(this.schedule.at / 60)}:${this.schedule.at % 60}`;
      },
      set(v) {
        const [hr, mn] = v.split(":");
        this.schedule.at = parseInt(hr) * 60 + parseInt(mn);
      },
    },
  },
};
</script>

<style scoped></style>
