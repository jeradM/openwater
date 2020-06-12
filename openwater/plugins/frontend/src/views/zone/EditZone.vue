<template>
  <ZoneForm :zoneData="zone" />
</template>

<script>
import ZoneForm from "../../components/zones/ZoneForm";
export default {
  name: "EditZone",
  components: { ZoneForm },
  computed: {
    zone() {
      const zone = this.$store.getters["zones/zoneObj"][this.$route.params.id];
      return JSON.parse(JSON.stringify(zone))
    },
  },
};
</script>

<style scoped></style>
