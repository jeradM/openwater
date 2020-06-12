import { format, parseISO } from "date-fns";

const SEC_PER_MIN = 60;
const MIN_PER_HOUR = 60;
// const HOUR_PER_DAY = 24;
// const MIN_PER_DAY = MIN_PER_HOUR * HOUR_PER_DAY;
const SEC_PER_HOUR = SEC_PER_MIN * MIN_PER_HOUR;
// const SEC_PER_DAY = SEC_PER_HOUR * HOUR_PER_DAY;

export const formatDateStr = (dateStr, length = "medium") => {
  const d = parseISO(dateStr);
  return dateToString(d, length);
};

export const dateToString = (date, length = "medium") => {
  let formatStr;
  if (length === "long") formatStr = "MMMM do, yyyy";
  else if (length === "medium") formatStr = "MMM d, yyyy";
  else if (length === "short") formatStr = "M/d/yyyy";
  return format(date, formatStr);
};

export const durationToString = (durationSec, length = "medium") => {
  const h = Math.floor(durationSec / SEC_PER_HOUR);
  const m = Math.floor((durationSec % SEC_PER_HOUR) / SEC_PER_MIN);
  const s = Math.floor(durationSec % SEC_PER_MIN);
  let hStr, mStr, sStr, sep;
  if (length === "long") {
    hStr = ` hour${h > 1 ? "s" : ""}`;
    mStr = ` minute${m > 1 ? "s" : ""}`;
    sStr = ` second${s > 1 ? "s" : ""}`;
    sep = ", ";
  } else if (length === "medium") {
    hStr = ` hr${h > 1 ? "s" : ""}`;
    mStr = ` min${m > 1 ? "s" : ""}`;
    sStr = ` sec${s > 1 ? "s" : ""}`;
    sep = " ";
  } else if (length === "short") {
    hStr = "H";
    mStr = "M";
    sStr = "S";
    sep = "";
  } else {
    throw Error(
      "durationToString: Invalid length choice. Must be one of ['long', 'medium', 'short']"
    );
  }
  let str = "";
  if (h > 0) {
    str += `${h}${hStr}`;
    if (m > 0 || s > 0) {
      str += sep;
    }
  }
  if (m > 0) {
    str += `${m}${mStr}`;
    if (s > 0) {
      str += sep;
    }
  }
  if (s > 0) {
    str += `${s}${sStr}`;
  }
  return str;
};
