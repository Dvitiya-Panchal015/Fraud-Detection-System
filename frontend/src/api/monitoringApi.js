import { apiGet, apiGetRoot } from "./axios.js";

export function getMonitoring() {
  return Promise.all([apiGet("/monitoring"), apiGetRoot("/health")]).then(
    ([monitoring, health]) => ({ ...monitoring, health }),
  );
}