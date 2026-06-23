import { useEffect, useRef, useCallback } from "react"
import L from "leaflet"

// Fix Leaflet's broken default icon paths when bundled with Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
})

const STATUS_COLORS = {
  DISCOVERED: "#facc15",
  CONFIRMED:  "#fb923c",
  ESCALATED:  "#60a5fa",
  RESOLVED:   "#34d399",
}

const STATUS_LABELS = {
  DISCOVERED: "Discovered by AI",
  CONFIRMED:  "Confirmed by citizens",
  ESCALATED:  "Escalated to govt",
  RESOLVED:   "Resolved",
}

const CATEGORY_ICONS = {
  POTHOLE:         "🕳️",
  STREETLIGHT:     "💡",
  WATER_LEAKAGE:   "💧",
  GARBAGE:         "🗑️",
  BROKEN_FOOTPATH: "🚶",
  DRAINAGE:        "🌊",
  TREE_FALLEN:     "🌳",
  ROAD_DAMAGE:     "🛣️",
  OTHER:           "⚠️",
}

// CartoDB Dark Matter — free, no key, looks premium
const TILE_URL = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'

function makeCircleMarker(issue) {
  const color = STATUS_COLORS[issue.status] || "#facc15"
  const isEscalated = issue.status === "ESCALATED"
  const isConfirmed = issue.status === "CONFIRMED"
  const radius = isEscalated ? 14 : isConfirmed ? 11 : 8

  return L.circleMarker([issue.latitude, issue.longitude], {
    radius,
    fillColor: color,
    fillOpacity: isEscalated ? 1 : 0.85,
    color: isEscalated ? "#ffffff" : "#111827",
    weight: isEscalated ? 2 : 1.5,
  })
}

export default function MapView({ issues, selectedIssue, onIssueSelect }) {
  const mapRef = useRef(null)
  const leafletMapRef = useRef(null)
  const markersRef = useRef([])
  const issuesRef = useRef(issues)

  useEffect(() => { issuesRef.current = issues }, [issues])

  const renderMarkers = useCallback((issueList) => {
    if (!leafletMapRef.current) return

    // Clear old markers
    markersRef.current.forEach((m) => m.remove())
    markersRef.current = []

    issueList.forEach((issue) => {
      const color = STATUS_COLORS[issue.status] || "#facc15"
      const icon = CATEGORY_ICONS[issue.category] || "⚠️"
      const marker = makeCircleMarker(issue)

      marker.bindPopup(`
        <div style="
          background:#111827;color:#fff;padding:10px 13px;border-radius:10px;
          min-width:200px;font-family:Inter,system-ui,sans-serif;
          border:1px solid #374151;font-size:13px;line-height:1.4
        ">
          <div style="font-weight:600;margin-bottom:3px">${icon} ${issue.title}</div>
          <div style="color:#9ca3af;font-size:11px;margin-bottom:8px">${issue.location_name || ""}</div>
          <div style="display:flex;align-items:center;justify-content:space-between">
            <span style="
              background:${color}18;color:${color};padding:2px 8px;
              border-radius:999px;border:1px solid ${color}35;font-size:10px;font-weight:500
            ">${issue.status}</span>
            <span style="color:#6b7280;font-size:11px">${issue.confirmation_count} confirmed</span>
          </div>
        </div>
      `, {
        className: "civicpulse-popup",
        maxWidth: 260,
        closeButton: false,
      })

      marker.on("click", () => onIssueSelect(issue))

      marker.addTo(leafletMapRef.current)
      markersRef.current.push(marker)
    })
  }, [onIssueSelect])

  // Init map once
  useEffect(() => {
    if (!mapRef.current || leafletMapRef.current) return

    leafletMapRef.current = L.map(mapRef.current, {
      center: [12.9716, 77.5946],
      zoom: 11,
      zoomControl: true,
    })

    L.tileLayer(TILE_URL, {
      attribution: TILE_ATTRIBUTION,
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(leafletMapRef.current)

    renderMarkers(issuesRef.current)

    return () => {
      if (leafletMapRef.current) {
        leafletMapRef.current.remove()
        leafletMapRef.current = null
      }
    }
  }, [renderMarkers])

  // Re-render markers when issues change
  useEffect(() => {
    if (leafletMapRef.current) renderMarkers(issues)
  }, [issues, renderMarkers])

  // Pan to selected issue
  useEffect(() => {
    if (!selectedIssue || !leafletMapRef.current) return
    leafletMapRef.current.flyTo(
      [selectedIssue.latitude, selectedIssue.longitude],
      14,
      { duration: 0.6 }
    )
  }, [selectedIssue])

  return (
    <div className="relative w-full h-full">
      <div ref={mapRef} className="w-full h-full" />

      {/* Legend */}
      <div className="absolute bottom-8 right-3 z-[1000] bg-gray-900/95 backdrop-blur-sm border border-gray-700 rounded-xl p-3 text-xs space-y-1.5 shadow-xl pointer-events-none">
        {Object.entries(STATUS_COLORS).map(([status, color]) => (
          <div key={status} className="flex items-center gap-2">
            <span
              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ background: color }}
            />
            <span className="text-gray-300">{STATUS_LABELS[status]}</span>
          </div>
        ))}
        <div className="pt-1 mt-1 border-t border-gray-700 text-gray-600">
          Click marker for details
        </div>
      </div>
    </div>
  )
}
