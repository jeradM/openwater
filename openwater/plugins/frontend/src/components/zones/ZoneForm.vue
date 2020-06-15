<template>
  <v-card max-width="800" class="mx-auto mt-2">
    <v-card-text>
      <v-form>
        <v-row>
          <v-col cols="9">
            <v-text-field
              v-model.trim="zoneData.name"
              label="Name"
              :error-messages="errors.name"
            />
          </v-col>
          <v-col cols="3">
            <v-checkbox
              v-model="zoneData.is_master"
              label="Master"
              :error-messages="errors.is_master"
            />
          </v-col>
          <v-col v-if="zoneData.is_master" cols="6">
            <v-text-field
              v-model.number="zoneData.open_offset"
              label="Open Offset"
              :error-messages="errors.open_offset"
            />
          </v-col>
          <v-col v-if="zoneData.is_master" cols="6">
            <v-text-field
              v-model.number="zoneData.close_offset"
              label="Close Offset"
              :error-messages="errors.close_offset"
            />
          </v-col>
          <v-col cols="12" sm="12">
            <v-select
              v-model="zoneData.zone_type"
              label="Zone Type"
              :items="zoneTypeList"
              :error-messages="errors.zone_type"
            />
          </v-col>
          <v-col v-if="!zoneData.is_master" cols="12" sm="12">
            <v-select
              v-model="zoneData.attrs.soil_type"
              label="Soil Type (Optional)"
              :items="soilTypes"
              item-text="name"
              item-value="id"
            />
          </v-col>
          <v-col v-if="!zoneData.is_master" cols="12" sm="12">
            <v-text-field
              v-model.number="zoneData.attrs.precip_rate"
              type="number"
              label="Precipitation Rate (Optional)"
            />
          </v-col>
          <v-col :key="attr.id" cols="12" sm="12" v-for="attr of zoneAttrs">
            <v-text-field
              v-model="zoneData.attrs[attr.id]"
              v-if="attr.type === 'text' || attr.type === 'number'"
              :type="attr.type"
              :label="attr.label"
              :error-messages="errors.attrs && errors.attrs[attr.id]"
            />
            <v-select
              v-model="zoneData.attrs[attr.id]"
              v-if="attr.type === 'select'"
              :label="attr.label"
              :items="attr.options"
              :error-messages="errors.attrs && errors.attrs[attr.id]"
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapGetters } from "vuex";
import { EventBus } from "../../utils/event-bus";
import { deleteZone, saveZone } from "../../utils/zones";

export default {
  name: "ZoneForm",
  data: () => ({
    // zoneData: { attrs: {} },
    errors: {},
  }),
  props: {
    zoneData: Object,
  },
  methods: {
    async save() {
      const resp = await saveZone(this.zoneData);
      const result = await resp.json();
      if (resp.status !== 200) {
        this.errors = result.errors;
        return;
      }
      this.goBack();
      this.errors = {};
      EventBus.$emit("snackbar", {
        msg: `Zone ${this.zone.id ? "Updated" : "Saved"}`,
      });
    },
    async deleteZone() {
      if (!confirm("Delete Zone?")) return;
      this.goBack();
      const res = await deleteZone(this.zoneData);
      const success = res.status === 204;
      const msg = success ? "Zone Deleted" : "Unable to delete zone";
      const type = success ? "success" : "error";
      EventBus.$emit("snackbar", { msg, type });
    },
    goBack() {
      this.$router.go(-1);
    },
  },
  computed: {
    ...mapGetters({
      zoneTypes: "zones/zoneTypes",
      zoneTypeList: "zones/zoneTypeList",
      soilTypes: "zones/soilTypes",
    }),
    zoneAttrs() {
      const selectedType = this.zoneTypes[this.zoneData.zone_type];
      return (selectedType && selectedType.attrs) || {};
    },
  },
  mounted() {
    // this.zoneData = { ...this.zone, attrs: { ...this.zone.attrs } };
    this.$store.commit("setSaveFunc", this.save);
  },
};
</script>

<style scoped></style>
