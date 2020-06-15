<template>
  <fragment>
    <h2 class="headline my-2">Steps</h2>
    <v-card class="mb-6">
      <v-card-text>
        <v-list>
          <draggable :list="steps">
            <ProgramStep
              v-for="(step, idx) in steps"
              :step="step"
              :idx="idx"
              :key="idx"
              :removeStep="removeStep"
            />
          </draggable>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="accent" @click="addStep">Add Step</v-btn>
      </v-card-actions>
    </v-card>
  </fragment>
</template>

<script>
import draggable from "vuedraggable";
import ProgramStep from "./ProgramStep";

export default {
  name: "ProgramSteps",
  components: {
    ProgramStep,
    draggable,
  },
  props: {
    steps: Array,
  },
  methods: {
    addStep() {
      this.steps.push({});
    },
    removeStep(idx) {
      this.steps = this.steps.splice(idx, 1);
    },
  },
};
</script>

<style scoped></style>
