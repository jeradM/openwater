<template>
  <fragment>
    <v-list-item class="programStep mb-0">
      <v-row align="center" no-gutters>
        <v-col cols="1">
          <v-icon class="handle">mdi-menu</v-icon>
          <!--          <v-avatar color="primary" size="22" dark>-->
          <!--            <span class="caption white&#45;&#45;text">{{ idx + 1 }}</span>-->
          <!--          </v-avatar>-->
        </v-col>
        <v-col>
          <v-row dense no-gutters class="mt-6">
            <v-col cols="12" sm="6" md="8" class="pl-3">
              <v-select
                multiple
                :value="step.zones"
                :items="allZones"
                item-value="id"
                item-text="name"
                label="Zone(s)"
                dense
              />
            </v-col>
            <v-col cols="6" sm="3" md="2" class="px-3">
              <v-text-field
                :value="minutes"
                @keyup="updateDurationMin"
                @change="updateDurationMin"
                label="Minutes"
                class="duration"
                dense
              />
            </v-col>
            <v-col cols="6" sm="3" md="2" class="pr-3">
              <v-text-field
                :value="seconds"
                @keyup="updateDurationSec"
                @change="updateDurationSec"
                label="Seconds"
                class="duration"
                dense
              />
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="1" class="text-right">
          <v-icon @click="removeStep(idx)" color="error"
            >mdi-delete-outline</v-icon
          >
        </v-col>
      </v-row>
    </v-list-item>
    <v-divider></v-divider>
  </fragment>
</template>

<script>
const getEventValue = (event) =>
  parseInt(typeof event === "string" ? event : event.target.value);

export default {
  name: "Step",
  props: {
    step: Object,
    idx: Number,
    removeStep: Function,
  },
  methods: {
    updateDurationMin(event) {
      const val = getEventValue(event) || 0;
      this.step.duration = val * 60 + (this.step.duration % 60);
    },
    updateDurationSec(event) {
      const val = getEventValue(event) || 0;
      this.step.duration = Math.floor(this.step.duration / 60) * 60 + val;
    },
  },
  computed: {
    allZones() {
      return this.$store.state.zones.all.filter((z) => !z.is_master);
    },
    minutes() {
      return Math.floor(this.step.duration / 60) || "";
    },
    seconds() {
      return this.step.duration % 60 || "";
    },
  },
};
</script>

<style scoped>
.handle {
  cursor: grab;
}
</style>
