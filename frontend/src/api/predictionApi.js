import { apiPost } from "./axios.js";

export async function predictTransaction(transaction) {
  return apiPost("/predict", transaction);
}