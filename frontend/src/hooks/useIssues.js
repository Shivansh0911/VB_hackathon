import { useState, useEffect, useCallback } from "react"
import { fetchIssues, fetchStats } from "../utils/api"

export function useIssues() {
  const [issues, setIssues] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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

  useEffect(() => { load() }, [load])

  return { issues, stats, loading, error, reload: load }
}
