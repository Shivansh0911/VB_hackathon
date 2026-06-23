import { useEffect, useRef, useCallback } from "react"

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

export default function MapView({ issues, selectedIssue, onIssueSelect }) {
  const mapRef = useRef(null)
  const googleMapRef = useRef(null)
  const markersRef = useRef([])
  const infoWindowRef = useRef(null)
  // Keep a ref to the latest issues so callbacks never go stale
  const issuesRef = useRef(issues)

  useEffect(() => {
    issuesRef.current = issues
  }, [issues])

  const renderMarkers = useCallback((issueList) => {
    if (!googleMapRef.current) return

    markersRef.current.forEach((m) => m.setMap(null))
    markersRef.current = []

    issueList.forEach((issue) => {
      const color = STATUS_COLORS[issue.status] || "#facc15"
      const icon = CATEGORY_ICONS[issue.category] || "⚠️"
      const isEscalated = issue.status === "ESCALATED"

      const marker = new window.google.maps.Marker({
        position: { lat: issue.latitude, lng: issue.longitude },
        map: googleMapRef.current,
        title: issue.title,
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          fillColor: color,
          fillOpacity: isEscalated ? 1 : 0.85,
          strokeColor: isEscalated ? "#ffffff" : "#111827",
          strokeWeight: isEscalated ? 2 : 1.5,
          scale: isEscalated ? 14 : issue.status === "CONFIRMED" ? 12 : 9,
        },
        zIndex: issue.confidence_score + (isEscalated ? 1000 : 0),
      })

      marker.addListener("click", () => {
        onIssueSelect(issue)
        infoWindowRef.current.setContent(`
          <div style="background:#111827;color:#fff;padding:12px 14px;border-radius:10px;min-width:210px;font-family:system-ui,sans-serif;border:1px solid #374151">
            <div style="font-size:13px;font-weight:600;margin-bottom:3px;line-height:1.3">${icon} ${issue.title}</div>
            <div style="font-size:11px;color:#9ca3af;margin-bottom:8px">${issue.location_name || ""}</div>
            <div style="display:flex;align-items:center;justify-content:space-between">
              <span style="background:${color}18;color:${color};padding:2px 8px;border-radius:999px;border:1px solid ${color}35;font-size:10px;font-weight:500">${issue.status}</span>
              <span style="color:#6b7280;font-size:11px">${issue.confirmation_count} confirmed</span>
            </div>
          </div>
        `)
        infoWindowRef.current.open(googleMapRef.current, marker)
      })

      markersRef.current.push(marker)
    })
  }, [onIssueSelect])

  const initMap = useCallback(() => {
    if (!mapRef.current || googleMapRef.current) return

    googleMapRef.current = new window.google.maps.Map(mapRef.current, {
      center: { lat: 12.9716, lng: 77.5946 },
      zoom: 11,
      styles: [
        { elementType: "geometry", stylers: [{ color: "#0f172a" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#0f172a" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
        { featureType: "road", elementType: "geometry", stylers: [{ color: "#1e293b" }] },
        { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#0f172a" }] },
        { featureType: "road.arterial", elementType: "labels.text.fill", stylers: [{ color: "#64748b" }] },
        { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#334155" }] },
        { featureType: "road.highway", elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
        { featureType: "water", elementType: "geometry", stylers: [{ color: "#020617" }] },
        { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#475569" }] },
        { featureType: "poi", stylers: [{ visibility: "off" }] },
        { featureType: "transit", stylers: [{ visibility: "off" }] },
        { featureType: "administrative", elementType: "geometry", stylers: [{ color: "#1e293b" }] },
        { featureType: "administrative.country", elementType: "labels.text.fill", stylers: [{ color: "#475569" }] },
        { featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{ color: "#64748b" }] },
      ],
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: true,
      zoomControl: true,
    })

    infoWindowRef.current = new window.google.maps.InfoWindow({
      pixelOffset: new window.google.maps.Size(0, -4),
    })

    // Render with current issues ref (avoids stale closure)
    renderMarkers(issuesRef.current)
  }, [renderMarkers])

  useEffect(() => {
    const apiKey = import.meta.env.VITE_MAPS_API_KEY
    if (!apiKey) return

    if (window.google?.maps) {
      initMap()
      return
    }

    const script = document.createElement("script")
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}`
    script.async = true
    script.defer = true
    script.onload = initMap
    document.head.appendChild(script)

    return () => {
      if (script.parentNode) script.parentNode.removeChild(script)
    }
  }, [initMap])

  // Re-render markers whenever issues change
  useEffect(() => {
    if (googleMapRef.current) renderMarkers(issues)
  }, [issues, renderMarkers])

  // Pan to selected issue
  useEffect(() => {
    if (!selectedIssue || !googleMapRef.current) return
    googleMapRef.current.panTo({ lat: selectedIssue.latitude, lng: selectedIssue.longitude })
    googleMapRef.current.setZoom(14)
  }, [selectedIssue])

  const hasKey = !!import.meta.env.VITE_MAPS_API_KEY

  return (
    <div className="relative w-full h-full">
      <div ref={mapRef} className="w-full h-full" />

      {/* Map Legend */}
      {hasKey && (
        <div className="absolute bottom-8 right-3 bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-xl p-3 text-xs space-y-1.5 shadow-xl">
          {Object.entries(STATUS_COLORS).map(([status, color]) => (
            <div key={status} className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full flex-shrink-0 border border-white/10"
                style={{ background: color }}
              />
              <span className="text-gray-300">{STATUS_LABELS[status]}</span>
            </div>
          ))}
        </div>
      )}

      {/* No-key fallback */}
      {!hasKey && (
        <div className="absolute inset-0 bg-gray-950 flex flex-col items-center justify-center text-gray-400">
          <div className="text-6xl mb-4 opacity-30">🗺️</div>
          <p className="text-sm font-medium text-white mb-1">Map requires API key</p>
          <p className="text-xs text-gray-500 mb-6">
            Add <code className="bg-gray-800 px-1 rounded">VITE_MAPS_API_KEY</code> to{" "}
            <code className="bg-gray-800 px-1 rounded">frontend/.env</code>
          </p>
          <div className="grid grid-cols-2 gap-3 w-80 max-h-64 overflow-y-auto">
            {issues.slice(0, 8).map((issue) => (
              <div
                key={issue.id}
                onClick={() => onIssueSelect(issue)}
                className="bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition border border-gray-700 hover:border-emerald-500/30"
              >
                <p className="text-white text-xs font-medium truncate leading-snug">
                  {CATEGORY_ICONS[issue.category]} {issue.title}
                </p>
                <p
                  className="text-xs mt-1 font-medium"
                  style={{ color: STATUS_COLORS[issue.status] || "#facc15" }}
                >
                  {issue.status}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
