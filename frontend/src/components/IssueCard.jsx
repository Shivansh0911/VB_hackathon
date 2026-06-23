import { useState } from "react"
import StatusBadge from "./StatusBadge"
import ConfirmModal from "./ConfirmModal"
import EscalationLog from "./EscalationLog"

const CATEGORY_ICONS = {
  POTHOLE:        "🕳️",
  STREETLIGHT:    "💡",
  WATER_LEAKAGE:  "💧",
  GARBAGE:        "🗑️",
  BROKEN_FOOTPATH:"🚶",
  DRAINAGE:       "🌊",
  TREE_FALLEN:    "🌳",
  ROAD_DAMAGE:    "🛣️",
  OTHER:          "⚠️",
}

export default function IssueCard({ issue, selected, onClick, onConfirmed }) {
  const [showConfirm, setShowConfirm] = useState(false)
  const [expanded, setExpanded] = useState(false)

  const handleClick = () => {
    onClick()
    setExpanded((v) => !v)
  }

  return (
    <>
      <div
        onClick={handleClick}
        className={`px-4 py-3 border-b border-gray-800/60 cursor-pointer transition-all hover:bg-gray-900/60 ${
          selected ? "bg-gray-900 border-l-2 border-l-emerald-500" : ""
        }`}
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-2.5 flex-1 min-w-0">
            <span className="text-xl mt-0.5 flex-shrink-0">{CATEGORY_ICONS[issue.category] || "⚠️"}</span>
            <div className="min-w-0">
              <p className="text-sm font-medium text-white truncate">{issue.title}</p>
              <p className="text-xs text-gray-500 truncate mt-0.5">{issue.location_name}</p>
            </div>
          </div>
          <StatusBadge status={issue.status} />
        </div>

        {/* Confidence bar */}
        <div className="flex items-center gap-3 mt-2 ml-9">
          <div className="flex-1 bg-gray-800 rounded-full h-1">
            <div
              className="bg-emerald-500 h-1 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(issue.confidence_score, 100)}%` }}
            />
          </div>
          <span className="text-xs text-gray-500 flex-shrink-0">
            {issue.confirmation_count} confirmed · {issue.confidence_score}%
          </span>
        </div>

        {/* Expanded detail */}
        {expanded && (
          <div className="mt-3 ml-9">
            <p className="text-xs text-gray-400 leading-relaxed mb-2">{issue.description}</p>
            <EscalationLog issue={issue} />
          </div>
        )}

        {/* Actions */}
        <div className="mt-2 ml-9 flex gap-2">
          {issue.status !== "ESCALATED" && issue.status !== "RESOLVED" && (
            <button
              onClick={(e) => { e.stopPropagation(); setShowConfirm(true) }}
              className="text-xs bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-3 py-1 rounded-md transition"
            >
              + Confirm
            </button>
          )}
          {issue.status === "ESCALATED" && (
            <span className="text-xs text-blue-400">
              ✓ Sent to {issue.authority_name}
            </span>
          )}
          {issue.status === "RESOLVED" && (
            <span className="text-xs text-green-400">✓ Resolved</span>
          )}
        </div>
      </div>

      {showConfirm && (
        <ConfirmModal
          issue={issue}
          onClose={() => setShowConfirm(false)}
          onSuccess={() => { setShowConfirm(false); onConfirmed() }}
        />
      )}
    </>
  )
}
