const CONFIG = {
  DISCOVERED: { label: "Discovered", color: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20" },
  CONFIRMED:  { label: "Confirmed",  color: "text-orange-400 bg-orange-400/10 border-orange-400/20" },
  ESCALATED:  { label: "Escalated",  color: "text-blue-400 bg-blue-400/10 border-blue-400/20" },
  RESOLVED:   { label: "Resolved",   color: "text-green-400 bg-green-400/10 border-green-400/20" },
}

export default function StatusBadge({ status }) {
  const c = CONFIG[status] || CONFIG.DISCOVERED
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium border flex-shrink-0 ${c.color}`}>
      {c.label}
    </span>
  )
}
