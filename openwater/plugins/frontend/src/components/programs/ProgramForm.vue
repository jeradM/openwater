<template>
  <v-form>
    <v-card class="mb-8">
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model.trim="program.name"
              label="Name"
              :error-messages="errors.name"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-select
              v-model="program.program_type"
              label="Program Type"
              :items="['Basic']"
              :error-messages="errors.zone_type"
            />
          </v-col>
          <v-col :key="attr.id" cols="12" sm="12" v-for="attr of program.attrs">
            <v-text-field
              v-model="program.attrs[attr.id]"
              v-if="attr.type === 'text' || attr.type === 'number'"
              :type="attr.type"
              :label="attr.label"
              :error-messages="errors.attrs && errors.attrs[attr.id]"
            />
            <v-select
              v-model="program.attrs[attr.id]"
              v-if="attr.type === 'select'"
              :label="attr.label"
              :items="attr.options"
              :error-messages="errors.attrs && errors.attrs[attr.id]"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-form>
</template>

<script>
export default {
  name: "ProgramForm",
  data: () => ({
    errors: {},
  }),
  props: {
    program: Object,
  },
  computed: {},
  methods: {
    // async save() {
    //   console.log(this.program);
    //   await saveProgram(this.program, this.steps, this.schedules);
    //   this.goBack();
    //   // this.errors = {};
    //   EventBus.$emit("snackbar", {
    //     msg: `Program ${this.program.id ? "Updated" : "Saved"}`,
    //   });
    // },
    // async deleteProgram() {
    //   this.goBack();
    // },
    // goBack() {
    //   this.$router.go(-1);
    // },
  },
};
</script>

<style scoped></style>
