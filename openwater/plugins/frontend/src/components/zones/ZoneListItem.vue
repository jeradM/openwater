<template>
  <v-expansion-panel>
    <v-expansion-panel-header>
      <template v-slot:default>
        <v-row>
          <v-col cols="auto" class="pa-1 me-4 d-flex">
            <v-icon :color="color">{{ icon }}</v-icon>
          </v-col>
          <v-col cols="auto" class="pa-1">
            <span class="subtitle-1" :class="textColor">{{ zone.name }}</span>
            <v-spacer></v-spacer>
            <span v-if="!zone.is_master" class="caption" :class="textColor">{{
              dateStr
            }}</span>
          </v-col>
        </v-row>
      </template>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn :to="editUrl" color="primary" text>Edit</v-btn>
        <v-btn v-if="showControlOpen" @click="turnOn(zone.id)" color="red" text
          >Turn On</v-btn
        >
        <v-btn
          v-if="showControlClose"
          @click="turnOff(zone.id)"
          color="red"
          text
          >Turn Off</v-btn
        >
      </v-card-actions>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import { secondsToDurationString, formatDateStr } from "../../utils/datetime";

const sendZoneCmd = async (id, cmd) => {
  return await fetch(`http://localhost:8000/api/zones/${id}/${cmd}`, {
    method: "post",
  });
};
export default {
  name: "ZoneListItem",
  props: {
    zone: Object,
  },
  computed: {
    showControlOpen() {
      return !this.zone.is_master && !this.zone.open;
    },
    showControlClose() {
      return !this.zone.is_master && this.zone.open;
    },
    editUrl() {
      return `/zones/edit/${this.zone.id}`;
    },
    dateStr() {
      if (!this.zone.last_run) return "No runs recorded";
      const run = this.zone.last_run;
      const dateStr = formatDateStr(run.start);
      const duration = secondsToDurationString(run.duration);
      return `Last Run: ${dateStr} for ${duration}`;
    },
    color() {
      return this.zone.open ? "primary" : "default";
    },
    textColor() {
      return this.color + "--text";
    },
    icon() {
      const o = this.zone.open;
      return this.zone.is_master
        ? o
          ? "mdi-valve-open"
          : "mdi-valve-closed"
        : o
        ? "mdi-sprinkler-variant"
        : "mdi-sprinkler";
    },
  },
  methods: {
    async turnOn(id) {
      await sendZoneCmd(id, "on");
      console.log(`Turned on zone: ${id}`);
    },
    async turnOff(id) {
      await sendZoneCmd(id, "off");
      console.log(`Turned on zone: ${id}`);
    },
  },
};
</script>

<style scoped></style>
