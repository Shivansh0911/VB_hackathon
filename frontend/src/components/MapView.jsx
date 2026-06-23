import { useEffect, useRef } from "react"

const STATUS_COLORS = {
  DISCOVERED: "#facc15",
  CONFIRMED:  "#fb923c",
  ESCALATED:  "#60a5fa",
  RESOLVED:   "#34d399",
}

const CATEGORY_ICONS = {
  POTHOLE: "🕳️", STREETLIGHT: "💡", WATER_LEAKAGE: "💧",
  GARBAGE: "🗑️", BROKEN_FOOTPATH: "🚶", DRAINAGE: "🌊",
  TREE_FALLEN: "🌳", ROAD_DAMAGE: "🛣️", OTHER: "⚠️",
}

export default function MapView({ issues, selectedIssue, onIssueSelect }) {
  const mapRef = useRef(null)
  const googleMapRef = useRef(null)
  const markersRef = useRef([])
  const infoWindowRef = useRef(null)

  useEffect(() => {
    const apiKey = import.meta.env.VITE_MAPS_API_KEY
    if (!apiKey) return

    if (window.google && window.google.maps) {
      initMap()
      return
    }

    const script = document.createElement("script")
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=marker`
    script.async = true
    script.onload = initMap
    document.head.appendChild(script)

    return () => {
      if (script.parentNode) script.parentNode.removeChild(script)
    }
  }, [])

  function initMap() {
    if (!mapRef.current || googleMapRef.current) return

    googleMapRef.current = new window.google.maps.Map(mapRef.current, {
      center: { lat: 12.9716, lng: 77.5946 },
      zoom: 11,
      styles: [
        { elementType: "geometry", stylers: [{ color: "#1a1a2e" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#1a1a2e" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#9e9e9e" }] },
        { featureType: "road", elementType: "geometry", stylers: [{ color: "#2d2d44" }] },
        { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#212121" }] },
        { featureType: "water", elementType: "geometry", stylers: [{ color: "#0e0e1a" }] },
        { featureType: "poi", stylers: [{ visibility: "off" }] },
        { featureType: "transit", stylers: [{ visibility: "off" }] },
      ],
      disableDefaultUI: false,
      mapTypeControl: false,
      streetViewControl: false,
    })

    infoWindowRef.current = new window.google.maps.InfoWindow()
    renderMarkers()
  }

  function renderMarkers() {
    if (!googleMapRef.current) return

    markersRef.current.forEach((m) => m.setMap(null))
    markersRef.current = []

    issues.forEach((issue) => {
      const color = STATUS_COLORS[issue.status] || "#facc15"
      const icon = CATEGORY_ICONS[issue.category] || "⚠️"

      const marker = new window.google.maps.Marker({
        position: { lat: issue.latitude, lng: issue.longitude },
        map: googleMapRef.current,
        title: issue.title,
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          fillColor: color,
          fillOpacity: 0.9,
          strokeColor: "#000",
          strokeWeight: 1.5,
          scale: issue.status === "ESCALATED" ? 14 : 10,
        },
        zIndex: issue.confidence_score,
      })

      marker.addListener("click", () => {
        onIssueSelect(issue)
        infoWindowRef.current.setContent(`
          <div style="background:#1f2937;color:#fff;padding:10px 12px;border-radius:8px;min-width:200px;font-family:sans-serif">
            <div style="font-size:13px;font-weight:600;margin-bottom:4px">${icon} ${issue.title}</div>
            <div style="font-size:11px;color:#9ca3af;margin-bottom:6px">${issue.location_name || ""}</div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11px">
              <span style="background:${color}20;color:${color};padding:2px 8px;border-radius:999px;border:1px solid ${color}40">${issue.status}</span>
              <span style="color:#6b7280">${issue.confirmation_count} confirmed</span>
            </div>
          </div>
        `)
        infoWindowRef.current.open(googleMapRef.current, marker)
      })

      markersRef.current.push(marker)
    })
  }

  useEffect(() => {
    if (googleMapRef.current) renderMarkers()
  }, [issues])

  useEffect(() => {
    if (!selectedIssue || !googleMapRef.current) return
    googleMapRef.current.panTo({ lat: selectedIssue.latitude, lng: selectedIssue.longitude })
    googleMapRef.current.setZoom(14)
  }, [selectedIssue])

  const hasKey = !!import.meta.env.VITE_MAPS_API_KEY

  return (
    <div className="relative w-full h-full">
      <div ref={mapRef} className="w-full h-full" />
      {!hasKey && (
        <div className="absolute inset-0 bg-gray-900 flex flex-col items-center justify-center text-gray-400">
          <div className="text-5xl mb-4">🗺️</div>
          <p className="text-sm font-medium text-white mb-1">Map not configured</p>
          <p className="text-xs">Add VITE_MAPS_API_KEY to .env to enable Google Maps</p>
          <div className="mt-6 grid grid-cols-2 gap-3 w-80">
            {issues.slice(0, 6).map((issue) => (
              <div
                key={issue.id}
                onClick={() => onIssueSelect(issue)}
                className="bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition text-xs"
              >
                <p className="text-white font-medium truncate">{issue.title}</p>
                <p className="text-gray-500 mt-0.5">{issue.status}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
