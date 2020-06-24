<template>
  <v-sheet max-width="1000" class="mx-auto">
    <ProgramForm :program="program" />
    <ProgramSteps :steps="steps" />
    <ProgramSchedules :schedules="schedules" />
  </v-sheet>
</template>

<script>
import ProgramForm from "../../components/programs/ProgramForm";
import { saveProgram } from "../../utils/programs";
import { EventBus } from "../../utils/event-bus";
import ProgramSteps from "../../components/programs/ProgramSteps";
import ProgramSchedules from "../../components/programs/ProgramSchedules";

export default {
  name: "EditProgram",
  data: () => ({
    program: {},
    steps: [],
  }),
  components: { ProgramForm, ProgramSteps, ProgramSchedules },
  methods: {
    async save() {
      await saveProgram(this.program, this.steps);
      this.$router.go(-1);
      EventBus.$emit("snackbar", {
        msg: "Program Updated",
      });
    },
  },
  computed: {
    schedules() {
      return this.$store.getters["schedules/forProgram"](this.program.id);
    },
  },
  beforeMount() {
    const id = parseInt(this.$route.params.id);
    const programs = this.$store.getters["programs/programObj"];
    const steps = this.$store.getters["programs/programSteps"](id);
    this.program = JSON.parse(JSON.stringify(programs[id]));
    this.steps = JSON.parse(JSON.stringify(steps));
  },
  mounted() {
    this.$store.commit("setSaveFunc", this.save);
  },
};
</script>

<style scoped></style>
