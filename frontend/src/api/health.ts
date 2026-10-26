import { apiGet } from "./client";

export interface Health {
  status: string;
}

export function getHealth(): Promise<Health> {
  return apiGet<Health>("/health");
}
