import { apiGet } from "./axios.js";

export function getAnalytics() {
  return apiGet("/analytics");
}