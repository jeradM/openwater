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
    <ProgramSteps :steps="program.steps" />
    <ProgramSchedules />
  </v-form>
</template>

<script>
import { EventBus } from "../../utils/event-bus";
import ProgramSteps from "./ProgramSteps";
import ProgramSchedules from "./ProgramSchedules";

export default {
  name: "ProgramForm",
  components: { ProgramSteps, ProgramSchedules },
  data: () => ({
    errors: {},
  }),
  props: {
    program: Object,
  },
  methods: {
    async save() {
      // const resp = await saveZone(this.zone);
      // const result = await resp.json();
      // if (resp.status !== 200) {
      //   this.errors = result.errors;
      //   return;
      // }
      this.goBack();
      // this.errors = {};
      EventBus.$emit("snackbar", {
        msg: `Zone ${this.zone.id ? "Updated" : "Saved"}`,
      });
    },
    async deleteProgram() {
      this.goBack();
      // const res = await deleteZone(this.zone);
      // const success = res.status === 204;
      // const msg = success ? "Zone Deleted" : "Unable to delete zone";
      // const type = success ? "success" : "error";
      // EventBus.$emit("snackbar", { msg, type });
    },
    goBack() {
      this.$router.go(-1);
    },
  },
  computed: {
    // ...mapGetters({
    //   zoneTypes: "zones/zoneTypes",
    //   zoneTypeList: "zones/zoneTypeList",
    //   soilTypes: "zones/soilTypes",
    // }),
    // zoneAttrs() {
    //   const selectedType = this.zoneTypes[this.zone.zone_type];
    //   return (selectedType && selectedType.attrs) || {};
    // },
  },
  mounted() {
    this.$store.commit("setSaveFunc", this.save);
  },
};
</script>

<style scoped></style>
