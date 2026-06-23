import { useState, useEffect, useCallback } from "react"
import { fetchIssues, fetchStats } from "../utils/api"

// Shown instantly while API loads — same as backend seed data
const FALLBACK_ISSUES = [
  { id: 1, title: "Large pothole on Indiranagar 100ft Road", category: "POTHOLE", status: "ESCALATED", latitude: 12.9784, longitude: 77.6408, location_name: "100ft Road, Indiranagar, Bengaluru", confidence_score: 85, confirmation_count: 7, description: "Deep pothole causing accidents near Indiranagar metro station.", source_signals: "[]", authority_name: "Bruhat Bengaluru Mahanagara Palike", escalation_letter: "Formal escalation letter sent.", escalation_sent_at: "2026-06-22 09:15:00" },
  { id: 2, title: "Streetlight outage Koramangala 5th Block", category: "STREETLIGHT", status: "CONFIRMED", latitude: 12.9352, longitude: 77.6245, location_name: "5th Block Junction, Koramangala, Bengaluru", confidence_score: 65, confirmation_count: 5, description: "Three consecutive streetlights non-functional for 5 days.", source_signals: "[]" },
  { id: 3, title: "Waterlogging blocks Andheri-Kurla Link Road", category: "DRAINAGE", status: "CONFIRMED", latitude: 19.1136, longitude: 72.8697, location_name: "Andheri-Kurla Link Road, Mumbai", confidence_score: 60, confirmation_count: 5, description: "Severe waterlogging due to blocked storm drains.", source_signals: "[]" },
  { id: 4, title: "Garbage overflow BTM Layout Sector 7", category: "GARBAGE", status: "DISCOVERED", latitude: 12.9166, longitude: 77.6101, location_name: "Sector 7, BTM Layout, Bengaluru", confidence_score: 25, confirmation_count: 1, description: "Municipal garbage not collected for 4 days.", source_signals: "[]" },
  { id: 5, title: "Water pipe burst on 80ft Road Koramangala", category: "WATER_LEAKAGE", status: "DISCOVERED", latitude: 12.9279, longitude: 77.6271, location_name: "80ft Road, Koramangala, Bengaluru", confidence_score: 30, confirmation_count: 2, description: "Underground pipe burst causing road flooding.", source_signals: "[]" },
  { id: 6, title: "Pothole craters near Bandra station west", category: "POTHOLE", status: "DISCOVERED", latitude: 19.0596, longitude: 72.8397, location_name: "Station Road West, Bandra, Mumbai", confidence_score: 20, confirmation_count: 1, description: "Multiple deep potholes on Station Road.", source_signals: "[]" },
  { id: 7, title: "Pothole cluster near Gachibowli circle", category: "POTHOLE", status: "DISCOVERED", latitude: 17.4401, longitude: 78.3489, location_name: "Gachibowli Circle, Hyderabad", confidence_score: 25, confirmation_count: 2, description: "Multiple potholes in a 100m stretch near Gachibowli.", source_signals: "[]" },
  { id: 8, title: "Broken footpath near Hitech City metro", category: "BROKEN_FOOTPATH", status: "DISCOVERED", latitude: 17.4478, longitude: 78.3762, location_name: "Metro Exit Gate 2, Hitech City, Hyderabad", confidence_score: 20, confirmation_count: 1, description: "Footpath tiles broken near metro exit gate 2.", source_signals: "[]" },
]

const FALLBACK_STATS = {
  total_issues: 8, discovered: 5, confirmed: 2, escalated: 1, resolved: 0, total_citizen_confirmations: 24,
}

export function useIssues() {
  const [issues, setIssues] = useState(FALLBACK_ISSUES)
  const [stats, setStats] = useState(FALLBACK_STATS)
  const [loading, setLoading] = useState(false)  // never block on load
  const [error, setError] = useState(null)
  const [liveUpdating, setLiveUpdating] = useState(true)  // start as updating

  const load = useCallback(async (silent = false) => {
    if (!silent) setLiveUpdating(true)
    try {
      setError(null)
      const [issueData, statsData] = await Promise.all([fetchIssues(), fetchStats()])
      if (issueData.issues?.length > 0) {
        setIssues(issueData.issues)
        setStats(statsData)
      }
    } catch (e) {
      // Keep showing fallback data — don't show error on first silent load
      if (!silent) setError(e.message)
    } finally {
      setLiveUpdating(false)
    }
  }, [])

  // Load real data immediately in background, fallback already visible
  useEffect(() => { load(true) }, [load])

  // Auto-refresh at 35s to pick up background discovery results
  useEffect(() => {
    const timer = setTimeout(() => load(true), 35000)
    return () => clearTimeout(timer)
  }, [load])

  return { issues, stats, loading, error, liveUpdating, reload: () => load(false) }
}
