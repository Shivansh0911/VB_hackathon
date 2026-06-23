export default function ImpactDashboard({ stats }) {
  const items = [
    { label: "Discovered", value: stats.discovered, color: "text-yellow-400" },
    { label: "Confirmed",  value: stats.confirmed,  color: "text-orange-400" },
    { label: "Escalated",  value: stats.escalated,  color: "text-blue-400"   },
    { label: "Resolved",   value: stats.resolved,   color: "text-green-400"  },
  ]

  return (
    <div className="px-4 py-3 border-b border-gray-800">
      <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Impact</p>
      <div className="grid grid-cols-4 gap-2">
        {items.map(({ label, value, color }) => (
          <div key={label} className="text-center">
            <p className={`text-xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-gray-500">{label}</p>
          </div>
        ))}
      </div>
      <div className="mt-2 flex items-center gap-1.5 text-xs text-gray-500">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
        {stats.total_citizen_confirmations} citizen confirmations received
      </div>
    </div>
  )
}
