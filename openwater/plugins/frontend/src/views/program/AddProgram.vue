<template>
  <ProgramForm :programData="program" />
</template>

<script>
import ProgramForm from "../../components/programs/ProgramForm";
export default {
  name: "AddProgram",
  data: () => ({
    program: {
      attrs: {},
    },
  }),
  components: { ProgramForm },
};
</script>

<style scoped></style>
