<template>
  <v-sheet>
    <v-btn
      to="/programs/add"
      color="secondary"
      fab
      absolute
      bottom
      right
      class="mb-12 mr-2"
    >
      <v-icon>mdi-plus</v-icon>
    </v-btn>
    <ProgramsList />
  </v-sheet>
</template>

<script>
import ProgramsList from "../../components/programs/ProgramsList";

export default {
  name: "Programs",
  components: { ProgramsList },
};
</script>

<style scoped></style>
