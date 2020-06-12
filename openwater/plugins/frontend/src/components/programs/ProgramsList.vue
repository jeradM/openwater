<template>
  <v-sheet max-width="800" class="mx-auto">
    <v-expansion-panels>
      <template v-for="program in programs">
        <ProgramsListItem :program="program" :key="program.id" />
      </template>
    </v-expansion-panels>
  </v-sheet>
</template>

<script>
import ProgramsListItem from "./ProgramsListItem";

export default {
  name: "ProgramsList",
  components: { ProgramsListItem },
  computed: {
    programs() {
      return this.$store.state.programs.all;
    },
  },
};
</script>

<style scoped></style>
