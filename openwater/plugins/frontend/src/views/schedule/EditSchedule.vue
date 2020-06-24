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
import ScheduleForm from "../../components/schedules/ScheduleForm";
import WeeklySchedule from "../../components/schedules/WeeklySchedule";
import IntervalSchedule from "../../components/schedules/IntervalSchedule";

export default {
  name: "EditProgram",
  components: { IntervalSchedule, WeeklySchedule, ScheduleForm },
  data: () => ({
    schedule: {},
  }),
  methods: {
    async save() {
      await this.$store.dispatch("schedules/saveSchedule", {
        schedule: this.schedule,
      });
      this.$router.go(-1);
      EventBus.$emit("snackbar", {
        msg: "Schedule Updated",
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
  beforeMount() {
    const id = parseInt(this.$route.params.id);
    const schedule = this.$store.state.schedules.all.find((s) => s.id === id);
    this.schedule = JSON.parse(JSON.stringify(schedule));
  },
  mounted() {
    this.$store.commit("setSaveFunc", this.save);
  },
};
</script>

<style scoped></style>
