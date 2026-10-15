import { apiRequest, toQuery } from "./apiClient";

// Builds list/get/create (and optional update/remove) helpers for a /api/v1 resource.
export const resource = (name) => ({
  list: (params) => apiRequest(`/api/v1/${name}${toQuery({ offset: 0, limit: 100, ...params })}`),
  get: (id) => apiRequest(`/api/v1/${name}/${id}`),
  create: (body) => apiRequest(`/api/v1/${name}`, { method: "POST", body: JSON.stringify(body) }),
  update: (id, body) => apiRequest(`/api/v1/${name}/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  remove: (id) => apiRequest(`/api/v1/${name}/${id}`, { method: "DELETE" }),
});
