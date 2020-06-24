<template>
  <v-menu
    ref="showTime"
    v-model="timeShown"
    :close-on-content-click="false"
    return-value.sync="_time"
    offset-y
  >
    <template v-slot:activator="{ attrs, on }">
      <v-text-field
        v-model="_time"
        :label="label"
        :disabled="disabled"
        readonly
        v-bind="attrs"
        v-on="on"
      />
    </template>
    <v-time-picker
      v-model="_time"
      full-width
      @click:minute="$refs.showTime.save(_time)"
    />
  </v-menu>
</template>

<script>
export default {
  name: "TimeInput",
  data: () => ({
    timeShown: false,
  }),
  props: {
    time: Number,
    label: String,
    disabled: Boolean,
  },
  computed: {
    _time: {
      get() {
        if (this.time == null) return null;
        const hrs = Math.floor(this.time / 60).toString();
        const mins = (this.time % 60).toString().padStart(2, "0");
        return `${hrs}:${mins}`;
      },
      set(v) {
        const [hr, mn] = v.split(":");
        const t = parseInt(hr) * 60 + parseInt(mn);
        this.$emit("updated", t);
      },
    },
  },
};
</script>

<style scoped></style>
