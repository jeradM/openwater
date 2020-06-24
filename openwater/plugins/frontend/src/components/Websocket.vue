<template>
  <span class="d-none" />
</template>
<script>
export default {
  name: "Websocket",

  data: () => ({
    ws: null,
  }),

  created() {
    this.ws = new WebSocket(`ws://${location.host}/ws`);

    this.ws.onopen = () => {
      console.log("WS: Connected");
    };

    this.ws.onmessage = (event) => {
      const d = JSON.parse(event.data);
      // console.log("Message Received: ", d);
      switch (d.type) {
        case "state.zones":
          this.$store.commit("zones/setZones", d.data.zones);
          break;
        case "state.programs":
          this.$store.commit("programs/setPrograms", d.data.programs);
          this.$store.commit("programs/setSteps", d.data.steps);
          break;
        case "state.schedules":
          this.$store.commit("schedules/setSchedules", d.data.schedules);
          break;
        case "state.all":
          this.$store.commit("zones/setZones", d.data.zones);
          this.$store.commit("programs/setPrograms", d.data.programs);
          this.$store.commit("programs/setSteps", d.data.steps);
          this.$store.commit("schedules/setSchedules", d.data.schedules);
          break;
        default:
          return;
      }
    };
  },
};
</script>

<style scoped></style>
