<template>
  <ZoneForm :zoneData="zone" />
</template>

<script>
import ZoneForm from "../../components/zones/ZoneForm";
export default {
  name: "AddZone",
  data: () => ({
    zone: {
      attrs: {},
    },
  }),
  components: { ZoneForm },
};
</script>

<style scoped></style>
