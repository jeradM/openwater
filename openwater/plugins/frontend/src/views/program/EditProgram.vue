<template>
  <v-sheet max-width="1000" class="mx-auto mt-2 pa-3" elevation="1">
    <ProgramForm :program="program" />
    <v-row>
      <v-col cols="12" sm="6">
        <ProgramSteps :steps="program.steps" />
      </v-col>
      <v-col cols="12" sm="6"> </v-col>
    </v-row>
  </v-sheet>
</template>

<script>
import ProgramForm from "../../components/programs/ProgramForm";
import ProgramSteps from "../../components/programs/ProgramSteps";

export default {
  name: "EditProgram",
  components: { ProgramSteps, ProgramForm },
  computed: {
    program() {
      const id = this.$route.params.id;
      const programs = this.$store.getters["programs/programObj"];
      return JSON.parse(JSON.stringify(programs[id]));
    },
  },
};
</script>

<style scoped></style>
