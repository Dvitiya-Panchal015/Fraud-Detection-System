import { apiGet } from "./axios.js";

export function getTransactions(params) {
  return apiGet("/transactions", params);
}