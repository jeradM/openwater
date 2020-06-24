import { minutesToDurationString, secondsToTimeString } from "./datetime";

export const SCHEDULE_TYPES = ["Weekly", "Interval", "Single"];

export const DAYS = [
  { val: 1, bit: 0, short: "Sun", long: "Sunday" },
  { val: 2, bit: 1, short: "Mon", long: "Monday" },
  { val: 4, bit: 2, short: "Tue", long: "Tuesday" },
  { val: 8, bit: 3, short: "Wed", long: "Wednesday" },
  { val: 16, bit: 4, short: "Thu", long: "Thursday" },
  { val: 32, bit: 5, short: "Fri", long: "Friday" },
  { val: 64, bit: 6, short: "Sat", long: "Saturday" },
];

export const DAY_RESTRICTION = [
  { label: "None", val: "" },
  { label: "Even", val: "E" },
  { label: "Odd", val: "O" },
];

export const getScheduleTitle = (schedule) => {
  let title = "";
  if (schedule.name) {
    title += `${schedule.name} - `;
  }
  title += schedule.schedule_type;
  return title;
};

export const getScheduleSubtitle = (schedule) => {
  let subtitle = "";
  switch (schedule.schedule_type) {
    case "Weekly":
      subtitle += getWeeklySubtitle(schedule);
      break;
    case "Interval":
      subtitle += getIntervalSubtitle(schedule);
      break;
    default:
      break;
  }
  return subtitle;
};

const getWeeklySubtitle = (schedule) => {
  if (schedule.dow_mask === 0) {
    return "No days selected to run";
  }
  let result = "";
  let days = [];
  DAYS.forEach((d) => {
    if (schedule.dow_mask & (1 << d.bit)) {
      days.push(d);
    }
  });
  if (schedule.dow_mask === 65) {
    result += "Weekends";
  } else if (schedule.dow_mask === 62) {
    result += "Weekdays";
  } else if (schedule.dow_mask === 127) {
    result += "Every day";
  } else if (days.length === 1) {
    result += `${days[0].long}s`;
  } else if (days.length === 2) {
    result += `${days[0].long}s and ${days[1].long}s`;
  } else {
    const dayStr = days.map((d) => d.short).join(", ");
    result += dayStr;
  }
  result += ` at ${secondsToTimeString(schedule.at)}`;
  return result;
};

const getIntervalSubtitle = (schedule) => {
  if (schedule.day_interval) {
    let result;
    if (schedule.day_interval === 1) {
      result = "Every day";
    } else {
      result = `Every ${schedule.day_interval} days`;
    }
    return result + ` at ${secondsToTimeString(schedule.at)}`;
  } else {
    return `Every ${minutesToDurationString(schedule.minute_interval, "long")}`;
  }
};

export const saveSchedule = async (schedule) => {
  let url = `http://${location.host}/api/schedules`;
  if (schedule.id) url += `/${schedule.id}`;
  const method = schedule.id ? "put" : "post";

  return await fetch(url, {
    method: method,
    header: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(schedule),
  });
};
