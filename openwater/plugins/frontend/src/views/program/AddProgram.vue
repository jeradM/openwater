<template>
  <v-sheet max-width="1000" class="mx-auto">
    <ProgramForm :program="program" />
    <ProgramSteps :steps="steps" />
  </v-sheet>
</template>

<script>
import ProgramForm from "../../components/programs/ProgramForm";
import { saveProgram } from "../../utils/programs";
import { EventBus } from "../../utils/event-bus";
import ProgramSteps from "../../components/programs/ProgramSteps";

export default {
  name: "EditProgram",
  data: () => ({
    program: { attrs: {} },
    steps: [],
  }),
  components: { ProgramForm, ProgramSteps },
  methods: {
    async save() {
      debugger;
      console.log(this.program);
      await saveProgram(this.program, this.steps);
      this.$router.go(-1);
      // this.errors = {};
      EventBus.$emit("snackbar", {
        msg: `Program ${this.program.id ? "Updated" : "Saved"}`,
      });
    },
  },
  mounted() {
    this.$store.commit("setSaveFunc", this.save);
  },
};
</script>

<style scoped></style>
