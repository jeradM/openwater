<template>
  <v-sheet max-width="800" class="mx-auto">
    <v-expansion-panels>
      <template v-for="zone in zones">
        <ZoneListItem :zone="zone" :key="zone.id" />
      </template>
    </v-expansion-panels>
  </v-sheet>
</template>

<script>
import ZoneListItem from "./ZoneListItem";

export default {
  name: "ZonesList",
  components: { ZoneListItem },
  computed: {
    zones() {
      return this.$store.state.zones.all;
    },
  },
};
</script>

<style scoped></style>
