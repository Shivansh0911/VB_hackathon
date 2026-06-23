export default function EscalationLog({ issue }) {
  if (!issue || issue.status !== "ESCALATED") return null

  return (
    <div className="mt-3 p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg text-xs">
      <p className="text-blue-400 font-medium mb-1">Escalation sent</p>
      <p className="text-gray-400">To: <span className="text-white">{issue.authority_name}</span></p>
      <p className="text-gray-400">Email: <span className="text-white">{issue.authority_email}</span></p>
      {issue.escalation_sent_at && (
        <p className="text-gray-500 mt-1">
          {new Date(issue.escalation_sent_at + "Z").toLocaleString("en-IN", {
            dateStyle: "medium",
            timeStyle: "short",
          })}
        </p>
      )}
      {issue.escalation_letter && (
        <details className="mt-2">
          <summary className="cursor-pointer text-blue-400 hover:text-blue-300">View letter</summary>
          <pre className="mt-2 text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
            {issue.escalation_letter}
          </pre>
        </details>
      )}
    </div>
  )
}
