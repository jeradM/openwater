<template>
  <v-sheet>
    <h2 class="headline my-2">Steps</h2>
    <draggable :list="st" group="steps" tag="v-list">
      <v-list-item v-for="step in st" :key="step.id">{{ step.id }}</v-list-item>
    </draggable>
  </v-sheet>
</template>

<script>
import draggable from "vuedraggable";
export default {
  name: "ProgramStep",
  components: {
    draggable,
  },
  data: () => ({
    st: [],
  }),
  props: {
    steps: Array,
  },
  mounted() {
    this.st = this.steps;
  },
};
</script>

<style scoped></style>
