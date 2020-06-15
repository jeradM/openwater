<template>
  <v-sheet max-width="1000" class="mx-auto">
    <ProgramForm :program="program" />
  </v-sheet>
</template>

<script>
import ProgramForm from "../../components/programs/ProgramForm";

export default {
  name: "EditProgram",
  data: () => ({
    program: {},
  }),
  components: { ProgramForm },
  beforeMount() {
    const id = this.$route.params.id;
    const programs = this.$store.getters["programs/programObj"];
    this.program = JSON.parse(JSON.stringify(programs[id]));
  },
};
</script>

<style scoped></style>
