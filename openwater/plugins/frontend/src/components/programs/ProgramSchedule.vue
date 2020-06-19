<template>
  <v-expansion-panel>
    <v-expansion-panel-header>
      <template v-slot:default>
        <span>
          {{ headerText }}
        </span>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <v-switch
          @click.capture.stop
          v-model="schedule.enabled"
          label="Enabled"
          class="flex-shrink-1 flex-grow-0 mr-8"
          dense
        />
      </template>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <v-row dense>
        <v-col cols="12" sm="6">
          <v-text-field v-model="schedule.name" label="Name" />
        </v-col>
        <v-col cols="12" sm="6">
          <v-select
            :items="scheduleTypes"
            v-model="schedule.schedule_type"
            label="Schedule Type"
          />
        </v-col>
      </v-row>
      <WeeklySchedule
        v-if="schedule.schedule_type === 'Weekly'"
        :schedule="schedule"
      />
    </v-expansion-panel-content>
    <v-divider></v-divider>
  </v-expansion-panel>
</template>

<script>
import WeeklySchedule from "./WeeklySchedule";
export default {
  name: "ProgramSchedule",
  components: { WeeklySchedule },
  props: {
    schedule: Object,
  },
  computed: {
    scheduleTypes() {
      console.log(this.schedule);
      return this.$store.state.scheduleTypes;
    },
    headerText() {
      let t = this.schedule.name;
      if (t) {
        return t + ` - ${this.schedule.schedule_type}`;
      }
      return this.schedule.schedule_type;
    },
  },
};
</script>

<style scoped></style>
