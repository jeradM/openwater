<template>
  <v-list-item class="programStep mb-0">
    <v-row align="center" no-gutters>
      <v-col cols="1">
        <v-icon class="handle">mdi-menu</v-icon>
      </v-col>
      <v-col>
        <v-row dense no-gutters class="mt-6">
          <v-col cols="12" sm="6" md="8" class="pl-3">
            <v-select
              v-model="step.zones"
              :items="allZones"
              item-value="id"
              item-text="name"
              label="Zone(s)"
              multiple
              dense
            />
          </v-col>
          <v-col cols="6" sm="3" md="2" class="px-3">
            <v-text-field
              v-model="minutes"
              label="Minutes"
              class="duration"
              dense
            />
          </v-col>
          <v-col cols="6" sm="3" md="2" class="pr-3">
            <v-text-field
              v-model="seconds"
              label="Seconds"
              class="duration"
              dense
            />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="1" class="text-right">
        <v-btn @click="removeStep(idx)" color="error" icon>
          <v-icon>mdi-delete-outline</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-list-item>
</template>

<script>
export default {
  name: "Step",
  props: {
    step: Object,
    idx: Number,
    removeStep: Function,
  },
  computed: {
    allZones() {
      return this.$store.state.zones.all.filter((z) => !z.is_master);
    },
    minutes: {
      get() {
        return this.step.duration ? Math.floor(this.step.duration / 60) : 0;
      },
      set(val) {
        const stepSecs = this.step.duration ? this.step.duration % 60 : 0;
        this.step.duration = parseInt(val || 0) * 60 + stepSecs;
        console.log("MInutes: ", this.step.duration);
      },
    },
    seconds: {
      get() {
        return this.step.duration % 60 || 0;
      },
      set(val) {
        const stepMin = this.step.duration
          ? Math.floor(this.step.duration / 60)
          : 0;
        this.step.duration = stepMin * 60 + parseInt(val);
        console.log("Seconds: ", this.step.duration);
      },
    },
  },
};
</script>

<style scoped>
.handle {
  cursor: grab;
}
</style>
