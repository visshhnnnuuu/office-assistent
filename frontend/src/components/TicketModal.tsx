import React, { useState, useEffect } from 'react'
import { Ticket, AlertTriangle, ShieldCheck, CheckCircle2, Clock, X, Send } from 'lucide-react'
import { createTicket, classifyTicketIntent, fetchUserTickets, ITTicket } from '@/lib/api'

interface TicketModalProps {
  isOpen: boolean
  onClose: () => void
  initialContext?: string
}

export default function TicketModal({
  isOpen,
  onClose,
  initialContext = ''
}: TicketModalProps) {
  const [activeTab, setActiveTab] = useState<'create' | 'list'>('create')
  const [description, setDescription] = useState(initialContext)
  const [summary, setSummary] = useState('')
  const [category, setCategory] = useState('VPN Issues')
  const [priority, setPriority] = useState('medium')
  const [deviceType, setDeviceType] = useState('Corporate Laptop')
  const [os, setOs] = useState('Windows 11 / macOS')
  const [errorMessage, setErrorMessage] = useState('')
  const [confirmed, setConfirmed] = useState(false)
  const [isSecurityIncident, setIsSecurityIncident] = useState(false)
  const [guidance, setGuidance] = useState('')
  const [tickets, setTickets] = useState<ITTicket[]>([])
  const [loading, setLoading] = useState(false)
  const [resultMsg, setResultMsg] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      loadTickets()
      if (initialContext) {
        setDescription(initialContext)
        handleClassify(initialContext)
      }
    }
  }, [isOpen, initialContext])

  const loadTickets = async () => {
    try {
      const data = await fetchUserTickets()
      setTickets(data)
    } catch {}
  }

  const handleClassify = async (text: string) => {
    if (!text || text.length < 5) return
    try {
      const res = await classifyTicketIntent(text)
      setCategory(res.intent.replace(/_/g, ' ').toUpperCase())
      setPriority(res.priority)
      setIsSecurityIncident(res.security_incident)
      setGuidance(res.safe_response_guidance)
    } catch {}
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!confirmed) {
      setErrorMsg('Explicit confirmation is strictly required to submit internal IT support tickets.')
      return
    }

    setLoading(true)
    setErrorMsg(null)
    setResultMsg(null)

    try {
      const res = await createTicket({
        category,
        summary: summary || description.slice(0, 50),
        description,
        priority,
        device_type: deviceType,
        operating_system: os,
        error_message: errorMessage,
        security_incident: isSecurityIncident,
        confirmed: true,
      })

      setResultMsg(`Ticket ${res.ticket_number} created successfully! Assigned to ${res.assigned_team}.`)
      setDescription('')
      setSummary('')
      setConfirmed(false)
      await loadTickets()
      setActiveTab('list')
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit IT ticket.')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div className="bg-claude-card border border-claude-border rounded-xl shadow-xl w-full max-w-xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-4 border-b border-claude-border flex items-center justify-between bg-claude-sidebar/50">
          <div className="flex items-center gap-2">
            <Ticket className="text-blue-600" size={18} />
            <div>
              <h2 className="font-semibold text-sm text-claude-text">IT Helpdesk & Ticketing</h2>
              <p className="text-[11px] text-claude-muted">Level-1 triage and support escalation</p>
            </div>
          </div>
          <button onClick={onClose} className="text-claude-muted hover:text-claude-text p-1">
            <X size={18} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-claude-border text-xs px-4 bg-claude-sidebar/20">
          <button
            onClick={() => setActiveTab('create')}
            className={`py-2 px-3 font-medium border-b-2 transition-colors ${
              activeTab === 'create'
                ? 'border-claude-accent text-claude-accent font-semibold'
                : 'border-transparent text-claude-muted hover:text-claude-text'
            }`}
          >
            Create New Ticket
          </button>
          <button
            onClick={() => setActiveTab('list')}
            className={`py-2 px-3 font-medium border-b-2 transition-colors ${
              activeTab === 'list'
                ? 'border-claude-accent text-claude-accent font-semibold'
                : 'border-transparent text-claude-muted hover:text-claude-text'
            }`}
          >
            My Open Tickets ({tickets.length})
          </button>
        </div>

        {/* Body Content */}
        <div className="p-4 overflow-y-auto flex-1 text-xs space-y-4">
          {errorMsg && (
            <div className="p-2.5 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg flex items-center gap-2">
              <AlertTriangle size={14} className="shrink-0 text-rose-600" />
              <span>{errorMsg}</span>
            </div>
          )}

          {resultMsg && (
            <div className="p-2.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg flex items-center gap-2">
              <CheckCircle2 size={14} className="shrink-0 text-emerald-600" />
              <span>{resultMsg}</span>
            </div>
          )}

          {activeTab === 'create' ? (
            <form onSubmit={handleSubmit} className="space-y-3">
              {isSecurityIncident && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-900 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-red-700">
                    <AlertTriangle size={15} />
                    <span>POTENTIAL SECURITY INCIDENT DETECTED</span>
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    Do NOT enter passwords or OTPs. Disconnect from Wi-Fi immediately. This ticket will be expedited directly to the Information Security Operations Center (ISOC).
                  </p>
                </div>
              )}

              {guidance && (
                <div className="p-2.5 bg-blue-50 border border-blue-200 rounded text-blue-900 text-[11px]">
                  <strong>Safe Level-1 Guidance:</strong> {guidance}
                </div>
              )}

              <div>
                <label className="block font-medium text-claude-text mb-1">Issue Description / Symptoms:</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Describe what occurred, error messages seen, and what applications were affected..."
                  value={description}
                  onChange={(e) => {
                    setDescription(e.target.value)
                    handleClassify(e.target.value)
                  }}
                  className="w-full p-2.5 bg-claude-card border border-claude-border rounded-md text-xs placeholder:text-claude-muted focus:outline-none focus:border-claude-accent"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-claude-text mb-1">Category:</label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full p-2 bg-claude-card border border-claude-border rounded-md text-xs focus:outline-none focus:border-claude-accent"
                  />
                </div>
                <div>
                  <label className="block font-medium text-claude-text mb-1">Assessed Priority:</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full p-2 bg-claude-card border border-claude-border rounded-md text-xs focus:outline-none focus:border-claude-accent"
                  >
                    <option value="critical">Critical (Incident / Work Blocked)</option>
                    <option value="high">High (Core Service Disrupted)</option>
                    <option value="medium">Medium (Standard Request)</option>
                    <option value="low">Low (Query / Accessory)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-claude-text mb-1">Device Type:</label>
                  <input
                    type="text"
                    value={deviceType}
                    onChange={(e) => setDeviceType(e.target.value)}
                    className="w-full p-2 bg-claude-card border border-claude-border rounded-md text-xs"
                  />
                </div>
                <div>
                  <label className="block font-medium text-claude-text mb-1">Operating System:</label>
                  <input
                    type="text"
                    value={os}
                    onChange={(e) => setOs(e.target.value)}
                    className="w-full p-2 bg-claude-card border border-claude-border rounded-md text-xs"
                  />
                </div>
              </div>

              {/* Explicit User Confirmation Checkbox */}
              <div className="pt-2 border-t border-claude-border">
                <label className="flex items-start gap-2 p-2 bg-claude-sidebar rounded border border-claude-border cursor-pointer">
                  <input
                    type="checkbox"
                    checked={confirmed}
                    onChange={(e) => setConfirmed(e.target.checked)}
                    className="mt-0.5 rounded border-claude-border text-claude-accent focus:ring-0"
                  />
                  <span className="text-[11px] text-claude-text leading-tight font-medium">
                    I explicitly confirm submission of this support ticket to IT Helpdesk. I verify that no passwords or personal credentials are included in this description.
                  </span>
                </label>
              </div>

              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  disabled={loading || !confirmed}
                  className="flex items-center gap-1.5 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg text-xs disabled:opacity-50 transition-colors shadow-xs"
                >
                  <Send size={13} />
                  <span>{loading ? 'Submitting...' : 'Submit IT Ticket'}</span>
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-2">
              {tickets.length === 0 ? (
                <div className="py-8 text-center text-claude-muted italic bg-claude-sidebar/30 rounded border border-dashed border-claude-border">
                  No IT tickets currently logged for your user profile.
                </div>
              ) : (
                tickets.map((t) => (
                  <div key={t.ticket_number} className="p-3 bg-claude-card border border-claude-border rounded-lg space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-claude-text font-mono text-xs">{t.ticket_number}</span>
                      <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                        t.priority === 'critical'
                          ? 'bg-rose-100 text-rose-800'
                          : (t.priority === 'high' ? 'bg-amber-100 text-amber-800' : 'bg-blue-50 text-blue-700')
                      }`}>
                        {t.priority}
                      </span>
                    </div>
                    <p className="font-medium text-claude-text text-xs">{t.summary}</p>
                    <div className="flex items-center justify-between text-[11px] text-claude-muted pt-1 border-t border-claude-border/40">
                      <span>Assigned: {t.assigned_team}</span>
                      <span className="flex items-center gap-1">
                        <Clock size={11} />
                        <span>Status: <strong className="uppercase">{t.status}</strong></span>
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
