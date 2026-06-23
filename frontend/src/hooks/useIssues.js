import { useState, useEffect, useCallback } from "react"
import { fetchIssues, fetchStats } from "../utils/api"

export function useIssues() {
  const [issues, setIssues] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [liveUpdating, setLiveUpdating] = useState(false)

  const load = useCallback(async () => {
    try {
      setError(null)
      const [issueData, statsData] = await Promise.all([fetchIssues(), fetchStats()])
      setIssues(issueData.issues || [])
      setStats(statsData)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial load
  useEffect(() => { load() }, [load])

  // Silent background refresh at 35s — picks up real discovery data
  // that background_discovery() adds after seed data is shown
  useEffect(() => {
    const timer = setTimeout(async () => {
      setLiveUpdating(true)
      await load()
      setLiveUpdating(false)
    }, 35000)
    return () => clearTimeout(timer)
  }, [load])

  return { issues, stats, loading, error, liveUpdating, reload: load }
}
