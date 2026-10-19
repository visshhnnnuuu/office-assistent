import React, { useState, useEffect } from 'react'
import { Brain, Trash2, Edit2, Plus, Check, AlertCircle, X, ShieldAlert } from 'lucide-react'
import { UserMemory, fetchMemories, addMemory, deleteMemory, deleteAllMemories, forgetConversation } from '@/lib/api'

interface MemoryModalProps {
  isOpen: boolean
  onClose: () => void
  currentSessionId?: string | null
  onConversationForgotten?: () => void
}

export default function MemoryModal({
  isOpen,
  onClose,
  currentSessionId,
  onConversationForgotten
}: MemoryModalProps) {
  const [memories, setMemories] = useState<UserMemory[]>([])
  const [loading, setLoading] = useState(false)
  const [newFact, setNewFact] = useState('')
  const [hasConsent, setHasConsent] = useState(true)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  const loadMemories = async () => {
    setLoading(true)
    try {
      const data = await fetchMemories()
      setMemories(data)
    } catch (err: any) {
      setErrorMsg('Failed to load memories.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen) {
      loadMemories()
      setErrorMsg(null)
      setSuccessMsg(null)
    }
  }, [isOpen])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newFact.trim()) return

    setErrorMsg(null)
    setSuccessMsg(null)
    try {
      await addMemory(newFact.trim(), hasConsent)
      setNewFact('')
      setSuccessMsg('Memory saved successfully with explicit consent.')
      await loadMemories()
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save memory.')
    }
  }

  const handleDeleteOne = async (id: string) => {
    try {
      await deleteMemory(id)
      setMemories(prev => prev.filter(m => m.memory_id !== id))
    } catch (err: any) {
      setErrorMsg('Failed to delete memory.')
    }
  }

  const handleDeleteAll = async () => {
    if (!confirm('Are you sure you want to permanently clear all personal preferences from memory?')) return
    try {
      await deleteAllMemories()
      setMemories([])
      setSuccessMsg('All preferences deleted.')
    } catch (err: any) {
      setErrorMsg('Failed to clear memories.')
    }
  }

  const handleForgetSession = async () => {
    if (!currentSessionId) return
    if (!confirm('Forget all message history for the current conversation?')) return
    try {
      await forgetConversation(currentSessionId)
      onConversationForgotten?.()
      onClose()
    } catch (err: any) {
      setErrorMsg('Failed to forget conversation.')
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div className="bg-claude-card border border-claude-border rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-4 border-b border-claude-border flex items-center justify-between bg-claude-sidebar/50">
          <div className="flex items-center gap-2">
            <Brain className="text-claude-accent" size={18} />
            <div>
              <h2 className="font-semibold text-sm text-claude-text">User Memory Settings</h2>
              <p className="text-[11px] text-claude-muted">Long-term personal preference management</p>
            </div>
          </div>
          <button onClick={onClose} className="text-claude-muted hover:text-claude-text p-1">
            <X size={18} />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-4 overflow-y-auto space-y-4 flex-1 text-xs">
          {errorMsg && (
            <div className="flex items-center gap-2 p-2.5 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg">
              <ShieldAlert size={14} className="shrink-0 text-rose-600" />
              <span>{errorMsg}</span>
            </div>
          )}

          {successMsg && (
            <div className="flex items-center gap-2 p-2.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg">
              <Check size={14} className="shrink-0 text-emerald-600" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Add New Memory Form */}
          <form onSubmit={handleAdd} className="space-y-2.5 bg-claude-sidebar/50 p-3 rounded-lg border border-claude-border">
            <label className="block font-medium text-claude-text text-xs">
              Add Preference (e.g., "Always reply with Python examples", "Prefers Malayalam answers"):
            </label>
            <input
              type="text"
              placeholder="Enter non-sensitive preference..."
              value={newFact}
              onChange={(e) => setNewFact(e.target.value)}
              className="w-full px-3 py-2 bg-claude-card border border-claude-border rounded-md text-xs placeholder:text-claude-muted focus:outline-none focus:border-claude-accent"
            />
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 text-[11px] text-claude-muted cursor-pointer">
                <input
                  type="checkbox"
                  checked={hasConsent}
                  onChange={(e) => setHasConsent(e.target.checked)}
                  className="rounded border-claude-border text-claude-accent focus:ring-0"
                />
                <span>Explicit User Consent Given</span>
              </label>

              <button
                type="submit"
                disabled={!newFact.trim()}
                className="flex items-center gap-1.5 py-1.5 px-3 bg-claude-accent hover:bg-claude-accentHover text-white font-medium rounded-md text-xs disabled:opacity-50 transition-colors"
              >
                <Plus size={13} />
                <span>Save</span>
              </button>
            </div>
            <p className="text-[10px] text-claude-muted flex items-center gap-1">
              <AlertCircle size={10} />
              <span>Passwords, salaries, credentials, and health data are blocked automatically.</span>
            </p>
          </form>

          {/* Saved Memories List */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-xs text-claude-text">
                Saved Preferences ({memories.length})
              </h3>
              {memories.length > 0 && (
                <button
                  onClick={handleDeleteAll}
                  className="text-[11px] text-rose-600 hover:text-rose-700 font-medium hover:underline"
                >
                  Delete All
                </button>
              )}
            </div>

            {loading ? (
              <div className="py-6 text-center text-claude-muted italic">Loading memories...</div>
            ) : memories.length === 0 ? (
              <div className="py-4 text-center text-claude-muted italic bg-claude-sidebar/30 rounded border border-dashed border-claude-border">
                No personal preferences saved.
              </div>
            ) : (
              <div className="space-y-1.5">
                {memories.map((m) => (
                  <div
                    key={m.memory_id}
                    className="flex items-center justify-between p-2.5 bg-claude-card border border-claude-border rounded-md hover:border-claude-borderDark transition-colors"
                  >
                    <span className="text-claude-text font-medium truncate mr-2">{m.fact}</span>
                    <button
                      onClick={() => handleDeleteOne(m.memory_id)}
                      className="text-claude-muted hover:text-rose-600 p-1 transition-colors"
                      title="Delete preference"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Forget Conversation Button */}
          {currentSessionId && (
            <div className="pt-2 border-t border-claude-border">
              <button
                onClick={handleForgetSession}
                className="w-full py-2 px-3 text-xs font-medium text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition-colors flex items-center justify-center gap-1.5"
              >
                <Trash2 size={13} />
                <span>Forget Current Conversation History</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
