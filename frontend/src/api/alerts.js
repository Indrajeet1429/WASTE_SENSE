import { apiRequest } from "./apiClient";
import { resource } from "./resource";

export const alertsApi = {
  ...resource("alerts"),
  updateStatus: (id, status) => apiRequest(`/api/v1/alerts/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
};
