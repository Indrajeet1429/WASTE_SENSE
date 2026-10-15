import { apiRequest } from "./apiClient";

export const getHealth = () => apiRequest("/api/v1/health");
export const getDatabaseHealth = () => apiRequest("/api/v1/health/database");
