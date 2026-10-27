import { apiGet } from "./client";
import type { FilterOptions } from "./types";

export function getFilterOptions(): Promise<FilterOptions> {
  return apiGet<FilterOptions>("/meta/filters");
}
