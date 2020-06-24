<template>
  <v-sheet>
    <v-btn
      to="/zones/add"
      color="secondary"
      fab
      fixed
      bottom
      right
      class="mr-2"
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
