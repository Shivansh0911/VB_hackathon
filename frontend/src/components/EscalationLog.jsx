import { useState } from "react"

export default function EscalationLog({ issue }) {
  const [showLetter, setShowLetter] = useState(false)

  if (!issue || issue.status !== "ESCALATED") return null

  const sentDate = issue.escalation_sent_at
    ? new Date(issue.escalation_sent_at + "Z").toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short",
      })
    : null

  return (
    <div className="mt-2 rounded-lg border border-blue-500/20 bg-blue-500/5 overflow-hidden">
      {/* Header */}
      <div className="px-3 py-2 flex items-start justify-between gap-2">
        <div>
          <div className="flex items-center gap-1.5 mb-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
            <p className="text-xs font-medium text-blue-400">Escalated</p>
          </div>
          <p className="text-xs text-gray-300">
            <span className="text-gray-500">To:</span> {issue.authority_name}
          </p>
          <p className="text-xs text-gray-500">{issue.authority_email}</p>
          {sentDate && (
            <p className="text-xs text-gray-600 mt-0.5">{sentDate}</p>
          )}
        </div>
        {issue.escalation_letter && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              setShowLetter((v) => !v)
            }}
            className="text-xs text-blue-400 hover:text-blue-300 flex-shrink-0 transition mt-0.5"
          >
            {showLetter ? "Hide" : "View letter"}
          </button>
        )}
      </div>

      {/* Letter content */}
      {showLetter && issue.escalation_letter && (
        <div className="border-t border-blue-500/15 px-3 py-2.5">
          <pre className="text-xs text-gray-300 whitespace-pre-wrap font-sans leading-relaxed max-h-48 overflow-y-auto">
            {issue.escalation_letter}
          </pre>
        </div>
      )}
    </div>
  )
}
