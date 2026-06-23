import { useState } from "react"
import { confirmIssue } from "../utils/api"

export default function ConfirmModal({ issue, onClose, onSuccess }) {
  const [photo, setPhoto] = useState(null)
  const [note, setNote] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState("")

  const handleSubmit = async () => {
    setLoading(true)
    setError("")
    try {
      const data = await confirmIssue(issue.id, photo, note)
      setResult(data)
    } catch (e) {
      setError(e.message || "Confirmation failed. Please try again.")
    }
    setLoading(false)
  }

  return (
    <div
      className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-sm p-5 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="font-semibold text-white mb-1">Confirm this issue</h3>
        <p className="text-sm text-gray-400 mb-4">{issue.title}</p>

        {!result ? (
          <>
            <label className="block text-xs text-gray-400 mb-1">
              Photo <span className="text-gray-600">(optional — AI validates)</span>
            </label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setPhoto(e.target.files?.[0] || null)}
              className="w-full text-xs text-gray-400 mb-3 file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:bg-gray-700 file:text-white file:cursor-pointer"
            />

            <label className="block text-xs text-gray-400 mb-1">Note <span className="text-gray-600">(optional)</span></label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Describe what you see..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg text-sm p-2 mb-4 resize-none h-20 text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500"
            />

            {error && <p className="text-red-400 text-xs mb-3">{error}</p>}

            <div className="flex gap-2">
              <button
                onClick={onClose}
                className="flex-1 text-sm py-2 rounded-lg border border-gray-700 hover:bg-gray-800 transition text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="flex-1 text-sm py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-semibold transition disabled:opacity-50"
              >
                {loading ? "Validating..." : "Confirm"}
              </button>
            </div>
          </>
        ) : (
          <div className="text-center py-4">
            <div className="text-4xl mb-3">{result.validation?.valid ? "✅" : "⚠️"}</div>
            <p className="text-sm font-medium text-white mb-1">
              {result.validation?.valid
                ? "Confirmed! Thank you."
                : "Photo didn't match — still recorded."}
            </p>
            <p className="text-xs text-gray-400 mb-1">{result.validation?.reasoning}</p>
            <p className="text-xs text-gray-500 mb-4">
              {result.new_confirmation_count} citizens confirmed &middot; {result.new_confidence_score}% confidence
            </p>
            {result.ready_for_escalation && (
              <p className="text-xs text-blue-400 mb-3">
                Threshold reached — escalating to authorities now
              </p>
            )}
            <button
              onClick={onSuccess}
              className="text-sm bg-gray-700 hover:bg-gray-600 px-5 py-2 rounded-lg transition text-white"
            >
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
