const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }))
    throw new Error(err.detail || "Request failed")
  }
  return res.json()
}

export const fetchIssues = (status) =>
  request(`/api/issues${status && status !== "ALL" ? `?status=${status}` : ""}`)

export const fetchIssue = (id) => request(`/api/issues/${id}`)

export const fetchStats = () => request("/api/stats")

export const confirmIssue = async (issueId, photo, citizenNote) => {
  const form = new FormData()
  form.append("citizen_note", citizenNote || "")
  if (photo) form.append("photo", photo)
  return request(`/api/confirm/${issueId}`, { method: "POST", body: form })
}

export const triggerDiscovery = () =>
  request("/api/admin/trigger-discovery", { method: "POST" })

export const triggerEscalation = () =>
  request("/api/admin/trigger-escalation", { method: "POST" })

export const escalateSingle = (id) =>
  request(`/api/admin/escalate/${id}`, { method: "POST" })
