<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    :return-value.sync="date_"
    transition="scale-transition"
    offset-y
    min-width="290px"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-text-field
        v-model="date_"
        :label="label"
        readonly
        v-bind="attrs"
        v-on="on"
      ></v-text-field>
    </template>
    <v-date-picker v-model="date_" no-title scrollable>
      <v-spacer></v-spacer>
      <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
      <v-btn text color="primary" @click="$refs.menu.save(date_)">OK</v-btn>
    </v-date-picker>
  </v-menu>
</template>

<script>
export default {
  name: "DateInput",
  data: () => ({
    menu: false,
  }),
  props: {
    date: String,
    label: String,
  },
  computed: {
    date_: {
      get() {
        return this.date;
      },
      set(val) {
        console.log("New Date: ", val);
        this.$emit("changed", val);
      },
    },
  },
};
</script>

<style scoped></style>
