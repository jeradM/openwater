<template>
  <v-sheet>
    <v-btn
      to="/zones/add"
      color="secondary"
      fab
      absolute
      bottom
      right
      class="mb-12 mr-2"
    >
      <v-icon>mdi-plus</v-icon>
    </v-btn>
    <ZonesList />
  </v-sheet>
</template>

<script>
import ZonesList from "../../components/zones/ZonesList";
export default {
  name: "Zones",
  components: { ZonesList },
};
</script>

<style scoped></style>
