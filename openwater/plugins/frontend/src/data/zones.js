export const zones = [
  {
    id: 1,
    name: "Master Zone 1",
    active: true,
    zone_type: "SHIFT_REGISTER",
    attrs: {
      sr_idx: 0,
    },
    last_run: {
      at: new Date(),
      duration: 300,
    },
    open: false,
  },
  {
    id: 2,
    name: "Test Zone 1",
    active: true,
    zone_type: "SHIFT_REGISTER",
    attrs: {
      sr_idx: 1,
      soil_type: "CLAY",
      precip_rate: 0.2,
    },
    last_run: {
      at: new Date(),
      duration: 900,
    },
    open: false,
  },
];
