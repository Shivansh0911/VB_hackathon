const STAT_CONFIG = [
  {
    key: "discovered",
    label: "Discovered",
    sublabel: "by AI",
    color: "text-yellow-400",
    bg: "bg-yellow-400/8",
    border: "border-yellow-400/20",
    dot: "bg-yellow-400",
  },
  {
    key: "confirmed",
    label: "Confirmed",
    sublabel: "by citizens",
    color: "text-orange-400",
    bg: "bg-orange-400/8",
    border: "border-orange-400/20",
    dot: "bg-orange-400",
  },
  {
    key: "escalated",
    label: "Escalated",
    sublabel: "to govt",
    color: "text-blue-400",
    bg: "bg-blue-400/8",
    border: "border-blue-400/20",
    dot: "bg-blue-400",
  },
  {
    key: "resolved",
    label: "Resolved",
    sublabel: "fixed",
    color: "text-green-400",
    bg: "bg-green-400/8",
    border: "border-green-400/20",
    dot: "bg-green-400",
  },
]

export default function ImpactDashboard({ stats }) {
  return (
    <div className="border-b border-gray-800">
      {/* Agent status bar */}
      <div className="flex items-center gap-3 px-4 py-2.5 bg-emerald-500/5 border-b border-emerald-500/10">
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-emerald-400 font-medium">3 agents active</span>
        </div>
        <span className="text-gray-700">·</span>
        <span className="text-xs text-gray-500">
          {stats.total_citizen_confirmations} confirmations received
        </span>
        <span className="text-gray-700">·</span>
        <span className="text-xs text-gray-500">{stats.total_issues} issues tracked</span>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-0 divide-x divide-gray-800">
        {STAT_CONFIG.map(({ key, label, sublabel, color, bg, border, dot }) => (
          <div key={key} className="px-3 py-3 text-center">
            <p className={`text-2xl font-bold tabular-nums ${color}`}>
              {stats[key]}
            </p>
            <p className="text-xs text-gray-400 mt-0.5 leading-none">{label}</p>
            <p className="text-xs text-gray-600 mt-0.5 leading-none">{sublabel}</p>
          </div>
        ))}
      </div>

      {/* Pipeline visual */}
      <div className="px-4 py-2.5 flex items-center gap-1 border-t border-gray-800/50">
        <span className="text-xs text-gray-600">Pipeline:</span>
        {[
          { label: "Discovery", color: "text-yellow-400" },
          { label: "→", color: "text-gray-700" },
          { label: "Confirmation", color: "text-orange-400" },
          { label: "→", color: "text-gray-700" },
          { label: "Resolution", color: "text-blue-400" },
          { label: "→", color: "text-gray-700" },
          { label: "Resolved", color: "text-green-400" },
        ].map((item, i) => (
          <span key={i} className={`text-xs ${item.color}`}>
            {item.label}
          </span>
        ))}
      </div>
    </div>
  )
}
