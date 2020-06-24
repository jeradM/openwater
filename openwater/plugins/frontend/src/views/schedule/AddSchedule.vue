<template>
  <v-sheet max-width="1000" class="mx-auto">
    <v-card class="mb-8">
      <v-form>
        <v-card-text>
          <ScheduleForm :schedule="schedule" />
          <WeeklySchedule v-if="weekly" :schedule="schedule" />
          <IntervalSchedule v-if="interval" :schedule="schedule" />
        </v-card-text>
      </v-form>
    </v-card>
  </v-sheet>
</template>

<script>
import { EventBus } from "../../utils/event-bus";
import WeeklySchedule from "../../components/schedules/WeeklySchedule";
import IntervalSchedule from "../../components/schedules/IntervalSchedule";
import ScheduleForm from "../../components/schedules/ScheduleForm";

export default {
  name: "EditProgram",
  components: { ScheduleForm, IntervalSchedule, WeeklySchedule },
  data: () => ({
    schedule: { enabled: true, at: null, start_day: null },
  }),
  methods: {
    async save() {
      console.log(this.schedule);
      await this.$store.dispatch("schedules/saveSchedule", {
        schedule: this.schedule,
      });
      this.$router.go(-1);
      EventBus.$emit("snackbar", {
        msg: `Schedule Saved`,
      });
    },
  },
  computed: {
    weekly() {
      return this.schedule.schedule_type === "Weekly";
    },
    interval() {
      return this.schedule.schedule_type === "Interval";
    },
    single() {
      return this.schedule.schedule_type === "Single";
    },
  },
  mounted() {
    this.$store.commit("setSaveFunc", this.save);
  },
};
</script>

<style scoped></style>
