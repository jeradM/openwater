export const getScheduleTitle = (schedule) => {
  let title = "";
  if (schedule.name) {
    title += `${schedule.name} - `;
  }
  title += schedule.schedule_type;
  return title;
};
