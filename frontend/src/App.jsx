import { useState } from "react"
import MapView from "./components/MapView"
import IssueCard from "./components/IssueCard"
import ImpactDashboard from "./components/ImpactDashboard"
import { useIssues } from "./hooks/useIssues"
import { triggerDiscovery, triggerEscalation } from "./utils/api"

const FILTERS = ["ALL", "DISCOVERED", "CONFIRMED", "ESCALATED", "RESOLVED"]

const AGENT_STEPS = [
  { icon: "📡", label: "Discovery", desc: "Twitter · Reddit · News RSS" },
  { icon: "✅", label: "Confirmation", desc: "Citizens validate" },
  { icon: "📨", label: "Resolution", desc: "Notifies authority" },
]

export default function App() {
  const { issues, stats, loading, error, reload } = useIssues()
  const [selectedIssue, setSelectedIssue] = useState(null)
  const [filter, setFilter] = useState("ALL")
  const [adminBusy, setAdminBusy] = useState(false)
  const [adminMsg, setAdminMsg] = useState("")
  const [adminSuccess, setAdminSuccess] = useState(false)

  const filteredIssues =
    filter === "ALL" ? issues : issues.filter((i) => i.status === filter)

  const handleAdmin = async (fn, label) => {
    setAdminBusy(true)
    setAdminSuccess(false)
    setAdminMsg(`${label} running...`)
    try {
      await fn()
      await reload()
      setAdminMsg(`${label} complete`)
      setAdminSuccess(true)
    } catch (e) {
      setAdminMsg(`Error: ${e.message}`)
      setAdminSuccess(false)
    }
    setAdminBusy(false)
    setTimeout(() => { setAdminMsg(""); setAdminSuccess(false) }, 4000)
  }

  return (
    <div className="h-screen flex flex-col bg-gray-950 text-white font-sans overflow-hidden">
      {/* ── Header ───────────────────────────────────────────────── */}
      <header className="border-b border-gray-800 px-5 py-2.5 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          {/* Logo */}
          <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-black font-bold text-sm select-none flex-shrink-0">
            CP
          </div>
          <div>
            <h1 className="text-sm font-semibold tracking-tight leading-none text-white">
              CivicPulse
            </h1>
            <p className="text-xs text-gray-500 mt-0.5 leading-none">
              AI discovers · Citizens confirm · Agents act
            </p>
          </div>

          {/* Agent pipeline chips */}
          <div className="hidden md:flex items-center gap-1 ml-4">
            {AGENT_STEPS.map((step, i) => (
              <div key={step.label} className="flex items-center gap-1">
                {i > 0 && <span className="text-gray-700 text-xs mx-0.5">→</span>}
                <div className="flex items-center gap-1.5 bg-gray-800 border border-gray-700 rounded-md px-2 py-1">
                  <span className="text-xs">{step.icon}</span>
                  <span className="text-xs text-gray-300 font-medium">{step.label}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {adminMsg && (
            <span className={`text-xs mr-1 ${adminSuccess ? "text-emerald-400" : "text-gray-400"}`}>
              {adminMsg}
            </span>
          )}
          <button
            onClick={() => handleAdmin(triggerDiscovery, "Discovery")}
            disabled={adminBusy}
            title="Manually trigger Agent 1 — scans signals and seeds new issues"
            className="text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-40 border border-gray-700 px-3 py-1.5 rounded-md transition"
          >
            {adminBusy ? "Running..." : "▶ Run Discovery"}
          </button>
          <button
            onClick={() => handleAdmin(triggerEscalation, "Escalation")}
            disabled={adminBusy}
            title="Manually trigger Agent 3 — escalates all confirmed issues"
            className="text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-40 border border-gray-700 px-3 py-1.5 rounded-md transition"
          >
            {adminBusy ? "Running..." : "▶ Run Escalation"}
          </button>
          <button
            onClick={reload}
            className="text-xs bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 px-3 py-1.5 rounded-md transition"
          >
            ↻ Refresh
          </button>
        </div>
      </header>

      {/* ── Body ─────────────────────────────────────────────────── */}
      {loading ? (
        <div className="flex-1 flex items-center justify-center text-gray-400">
          <div className="text-center">
            <div className="w-10 h-10 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm font-medium text-white mb-1">Discovery agent running</p>
            <p className="text-xs text-gray-500">Scanning Twitter · Reddit · Google News · Clustering signals</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-sm">
            <div className="text-4xl mb-3">⚠️</div>
            <p className="text-sm font-medium text-red-400 mb-1">Backend unreachable</p>
            <p className="text-xs text-gray-500 mb-1">{error}</p>
            <p className="text-xs text-gray-600 mb-5">
              Make sure the FastAPI server is running on port 8000 and{" "}
              <code className="bg-gray-800 px-1 rounded">VITE_API_URL</code> is set correctly.
            </p>
            <button
              onClick={reload}
              className="text-sm bg-gray-800 hover:bg-gray-700 border border-gray-700 px-5 py-2 rounded-lg transition text-white"
            >
              Retry
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-1 min-h-0">
          {/* ── Left panel ─────────────────────────────────────── */}
          <div className="w-96 flex-shrink-0 border-r border-gray-800 flex flex-col min-h-0">
            {stats && <ImpactDashboard stats={stats} />}

            {/* Filter tabs */}
            <div className="flex gap-1 px-3 py-2.5 border-b border-gray-800 flex-wrap flex-shrink-0">
              {FILTERS.map((s) => {
                const count =
                  s === "ALL"
                    ? issues.length
                    : issues.filter((i) => i.status === s).length
                return (
                  <button
                    key={s}
                    onClick={() => setFilter(s)}
                    className={`text-xs px-2.5 py-1 rounded-md transition ${
                      filter === s
                        ? "bg-emerald-500 text-black font-semibold"
                        : "text-gray-400 hover:text-white hover:bg-gray-800"
                    }`}
                  >
                    {s === "ALL"
                      ? `All (${count})`
                      : `${s.charAt(0) + s.slice(1).toLowerCase()} (${count})`}
                  </button>
                )
              })}
            </div>

            {/* Issue list */}
            <div className="flex-1 overflow-y-auto">
              {filteredIssues.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-600 gap-2 px-6 text-center">
                  <span className="text-3xl opacity-30">📡</span>
                  {filter === "ALL" ? (
                    <>
                      <p className="text-sm text-gray-400">No issues detected yet</p>
                      <p className="text-xs text-gray-600">Click <span className="text-gray-400 font-medium">▶ Run Discovery</span> to scan live signals from Twitter, Reddit &amp; Google News</p>
                    </>
                  ) : (
                    <>
                      <p className="text-sm">No issues in this category</p>
                      <button
                        onClick={() => setFilter("ALL")}
                        className="text-xs text-emerald-400 hover:text-emerald-300 mt-1"
                      >
                        Show all issues
                      </button>
                    </>
                  )}
                </div>
              ) : (
                filteredIssues.map((issue) => (
                  <IssueCard
                    key={issue.id}
                    issue={issue}
                    selected={selectedIssue?.id === issue.id}
                    onClick={() => setSelectedIssue(issue)}
                    onConfirmed={reload}
                  />
                ))
              )}
            </div>
          </div>

          {/* ── Map ────────────────────────────────────────────── */}
          <div className="flex-1 min-w-0 relative">
            <MapView
              issues={filteredIssues}
              selectedIssue={selectedIssue}
              onIssueSelect={(issue) => {
                setSelectedIssue(issue)
                // Also update filter to show selected issue's status bucket if in a filter
                if (filter !== "ALL" && issue.status !== filter) {
                  setFilter("ALL")
                }
              }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
