import { useState } from "react"
import MapView from "./components/MapView"
import IssueCard from "./components/IssueCard"
import ImpactDashboard from "./components/ImpactDashboard"
import { useIssues } from "./hooks/useIssues"
import { triggerDiscovery, triggerEscalation } from "./utils/api"

const FILTERS = ["ALL", "DISCOVERED", "CONFIRMED", "ESCALATED", "RESOLVED"]

export default function App() {
  const { issues, stats, loading, error, reload } = useIssues()
  const [selectedIssue, setSelectedIssue] = useState(null)
  const [filter, setFilter] = useState("ALL")
  const [adminBusy, setAdminBusy] = useState(false)
  const [adminMsg, setAdminMsg] = useState("")

  const filteredIssues =
    filter === "ALL" ? issues : issues.filter((i) => i.status === filter)

  const handleAdmin = async (fn, label) => {
    setAdminBusy(true)
    setAdminMsg(`Running ${label}...`)
    try {
      await fn()
      await reload()
      setAdminMsg(`${label} complete`)
    } catch (e) {
      setAdminMsg(`Error: ${e.message}`)
    }
    setAdminBusy(false)
    setTimeout(() => setAdminMsg(""), 3000)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white font-sans">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-black font-bold text-sm select-none">
            CP
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight leading-none">CivicPulse</h1>
            <p className="text-xs text-gray-500 mt-0.5">AI discovers. Citizens confirm. Agents act.</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {adminMsg && (
            <span className="text-xs text-gray-400 mr-2">{adminMsg}</span>
          )}
          <button
            onClick={() => handleAdmin(triggerDiscovery, "Discovery")}
            disabled={adminBusy}
            className="text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-40 px-3 py-1.5 rounded-md transition"
            title="Manually trigger the discovery agent"
          >
            Run Discovery
          </button>
          <button
            onClick={() => handleAdmin(triggerEscalation, "Escalation")}
            disabled={adminBusy}
            className="text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-40 px-3 py-1.5 rounded-md transition"
            title="Escalate all confirmed issues"
          >
            Run Escalation
          </button>
          <button
            onClick={reload}
            className="text-xs bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 px-3 py-1.5 rounded-md transition"
          >
            Refresh
          </button>
        </div>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-[calc(100vh-57px)] text-gray-400">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm">Discovery agent scanning signals...</p>
          </div>
        </div>
      ) : error ? (
        <div className="flex items-center justify-center h-[calc(100vh-57px)]">
          <div className="text-center text-red-400">
            <p className="text-sm font-medium mb-2">Failed to connect to backend</p>
            <p className="text-xs text-gray-500 mb-4">{error}</p>
            <button onClick={reload} className="text-xs bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-md transition text-white">
              Retry
            </button>
          </div>
        </div>
      ) : (
        <div className="flex h-[calc(100vh-57px)]">
          {/* Left panel */}
          <div className="w-96 border-r border-gray-800 flex flex-col flex-shrink-0">
            {stats && <ImpactDashboard stats={stats} />}

            {/* Filter tabs */}
            <div className="flex gap-1 px-4 py-2.5 border-b border-gray-800 flex-wrap">
              {FILTERS.map((s) => {
                const count = s === "ALL"
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
                    {s === "ALL" ? `All (${count})` : `${s.charAt(0) + s.slice(1).toLowerCase()} (${count})`}
                  </button>
                )
              })}
            </div>

            {/* Issue list */}
            <div className="flex-1 overflow-y-auto">
              {filteredIssues.length === 0 ? (
                <div className="text-center py-16 text-gray-600">
                  <p className="text-sm">No issues in this category</p>
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

          {/* Map */}
          <div className="flex-1 min-w-0">
            <MapView
              issues={filteredIssues}
              selectedIssue={selectedIssue}
              onIssueSelect={setSelectedIssue}
            />
          </div>
        </div>
      )}
    </div>
  )
}
