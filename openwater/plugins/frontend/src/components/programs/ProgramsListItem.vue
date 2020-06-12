<template>
  <v-expansion-panel>
    <v-expansion-panel-header>
      <template v-slot:default>
        <v-row>
          <v-col cols="1" class="pa-1 d-flex">
            <v-icon>mdi-clock-outline</v-icon>
          </v-col>
          <v-col cols="11" class="pa-1">
            <v-row>
              <span class="subtitle-1">{{ program.name }}</span>
            </v-row>
          </v-col>
        </v-row>
      </template>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn :to="editUrl" color="primary" text>Edit</v-btn>
      </v-card-actions>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
export default {
  name: "ProgramsListItem",
  props: {
    program: Object,
  },
  computed: {
    editUrl() {
      return `/programs/edit/${this.program.id}`;
    },
  },
};
</script>

<style scoped></style>
