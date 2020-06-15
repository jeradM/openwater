<template>
  <fragment>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <template v-slot:default>
          <span>
            {{ headerText }}
          </span>
        </template>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-row>
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
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-divider></v-divider>
  </fragment>
</template>

<script>
export default {
  name: "ProgramSchedule",
  props: {
    schedule: Object,
  },
  computed: {
    scheduleTypes() {
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

<style scoped>
.invisible {
  visibility: hidden;
}
</style>
