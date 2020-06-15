<template>
  <ZoneForm :zoneData="zone" />
</template>

<script>
import ZoneForm from "../../components/zones/ZoneForm";
export default {
  name: "EditZone",
  components: { ZoneForm },
  data: () => ({
    zone: {},
  }),
  beforeMount() {
    const id = this.$route.params.id;
    const zones = this.$store.getters["zones/zoneObj"];
    this.zone = JSON.parse(JSON.stringify(zones[id]));
  },
};
</script>

<style scoped></style>
