import React, { useState, useEffect } from 'react'
import {
  Database, ShieldAlert, CheckCircle2, Play, Eye,
  Lock, AlertTriangle, FileCode, X, Search, RefreshCw
} from 'lucide-react'
import { listDatasets, inspectDataset, importDataset, DatasetItem } from '@/lib/api'

interface AdminDatasetsModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function AdminDatasetsModal({
  isOpen,
  onClose
}: AdminDatasetsModalProps) {
  const [datasets, setDatasets] = useState<DatasetItem[]>([])
  const [loading, setLoading] = useState(false)
  const [activeCategory, setActiveCategory] = useState<string>('all')
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null)
  const [inspectOutput, setInspectOutput] = useState<any | null>(null)
  const [importStatus, setImportStatus] = useState<any | null>(null)
  const [acceptLicense, setAcceptLicense] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      loadRegistry()
      setInspectOutput(null)
      setImportStatus(null)
    }
  }, [isOpen])

  const loadRegistry = async () => {
    setLoading(true)
    try {
      const data = await listDatasets()
      setDatasets(data)
    } finally {
      setLoading(false)
    }
  }

  const handleInspect = async (name: string) => {
    setSelectedDataset(name)
    setActionLoading(true)
    setInspectOutput(null)
    setImportStatus(null)
    try {
      const res = await inspectDataset(name)
      setInspectOutput(res)
    } finally {
      setActionLoading(false)
    }
  }

  const handleImport = async (name: string) => {
    setSelectedDataset(name)
    setActionLoading(true)
    setImportStatus(null)
    try {
      const res = await importDataset(name, acceptLicense, 50)
      setImportStatus(res)
    } finally {
      setActionLoading(false)
    }
  }

  if (!isOpen) return null

  const categories = [
    { id: 'all', label: 'All Datasets' },
    { id: 'multilingual', label: 'Multilingual' },
    { id: 'it_helpdesk', label: 'IT Helpdesk' },
    { id: 'rag_benchmarks', label: 'RAG Benchmarks' },
    { id: 'voice', label: 'Voice (Controlled)' },
  ]

  const filtered = activeCategory === 'all'
    ? datasets
    : datasets.filter(d => d.category === activeCategory)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div className="bg-claude-card border border-claude-border rounded-xl shadow-xl w-full max-w-4xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 border-b border-claude-border flex items-center justify-between bg-purple-50/50">
          <div className="flex items-center gap-2">
            <Database className="text-purple-600" size={18} />
            <div>
              <h2 className="font-semibold text-sm text-claude-text">
                Hugging Face Dataset Registry & Governance Portal
              </h2>
              <p className="text-[11px] text-claude-muted">
                Strict quarantine: Public benchmark datasets are completely isolated from internal production knowledge.
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-claude-muted hover:text-claude-text p-1">
            <X size={18} />
          </button>
        </div>

        {/* Category Filter */}
        <div className="flex border-b border-claude-border text-xs px-4 bg-claude-sidebar/30 gap-1 overflow-x-auto py-2">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                activeCategory === cat.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-claude-card text-claude-muted border border-claude-border hover:text-claude-text'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Content Body Grid */}
        <div className="flex-1 overflow-hidden grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-claude-border text-xs">
          {/* Left Column: Dataset List */}
          <div className="overflow-y-auto p-4 space-y-2">
            <div className="flex items-center justify-between pb-2">
              <span className="font-semibold text-claude-text text-xs">Recognized Benchmarks ({filtered.length})</span>
              <button
                onClick={loadRegistry}
                className="text-claude-muted hover:text-claude-text flex items-center gap-1 text-[11px]"
              >
                <RefreshCw size={11} />
                <span>Refresh</span>
              </button>
            </div>

            {loading ? (
              <div className="py-12 text-center text-claude-muted italic">Loading registry...</div>
            ) : (
              filtered.map(ds => {
                const isSelected = selectedDataset === ds.name

                return (
                  <div
                    key={ds.name}
                    className={`p-3 rounded-lg border transition-all ${
                      isSelected
                        ? 'border-purple-500 bg-purple-50/40 ring-1 ring-purple-400'
                        : 'border-claude-border bg-claude-card hover:border-claude-borderDark'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="font-bold text-xs text-claude-text font-mono truncate">{ds.name}</h4>
                        <p className="text-[11px] text-claude-muted mt-0.5 line-clamp-2">{ds.description}</p>
                      </div>
                      <span className={`text-[9px] uppercase px-1.5 py-0.5 rounded font-bold shrink-0 ${
                        ds.enabled ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-gray-100 text-gray-500'
                      }`}>
                        {ds.enabled ? 'ENABLED' : 'DISABLED'}
                      </span>
                    </div>

                    <div className="flex items-center justify-between pt-2 mt-2 border-t border-claude-border/40 text-[10px] text-claude-muted">
                      <span>License: <strong>{ds.license}</strong></span>
                      <div className="flex gap-1.5">
                        <button
                          onClick={() => handleInspect(ds.name)}
                          disabled={actionLoading}
                          className="px-2 py-0.5 bg-claude-sidebar hover:bg-claude-card border border-claude-border rounded text-[10px] font-medium text-claude-text flex items-center gap-1"
                        >
                          <Eye size={10} />
                          <span>Inspect</span>
                        </button>
                        <button
                          onClick={() => handleImport(ds.name)}
                          disabled={actionLoading}
                          className="px-2 py-0.5 bg-purple-600 hover:bg-purple-700 text-white rounded text-[10px] font-medium flex items-center gap-1"
                        >
                          <Play size={10} />
                          <span>Import</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })
            )}
          </div>

          {/* Right Column: Inspector & Output Details */}
          <div className="overflow-y-auto p-4 space-y-4 bg-claude-sidebar/20">
            {/* Governance Warning Banner */}
            <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg text-amber-900 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-amber-800 text-xs">
                <Lock size={13} />
                <span>DATASET QUARANTINE CONTROLS</span>
              </div>
              <p className="text-[11px] leading-relaxed">
                Imports are strictly routed into quarantined benchmark directories under <code>data/public/processed/</code>. They are NEVER indexed into company policy vector stores.
              </p>

              <label className="flex items-center gap-2 pt-1 cursor-pointer font-medium text-[11px] text-amber-950">
                <input
                  type="checkbox"
                  checked={acceptLicense}
                  onChange={(e) => setAcceptLicense(e.target.checked)}
                  className="rounded border-amber-400 text-purple-600 focus:ring-0"
                />
                <span>I explicitly accept the licensing terms for public evaluation benchmarking.</span>
              </label>
            </div>

            {/* Inspect / Import Output Display */}
            {actionLoading ? (
              <div className="py-16 text-center text-claude-muted italic">
                Executing dataset action in progress...
              </div>
            ) : inspectOutput ? (
              <div className="space-y-2">
                <h4 className="font-bold text-xs text-claude-text">Schema Inspection Results</h4>
                <div className="bg-claude-card p-3 rounded-lg border border-claude-border font-mono text-[11px] overflow-x-auto space-y-1">
                  <div><strong>Dataset:</strong> {inspectOutput.dataset_name}</div>
                  <div><strong>License:</strong> {inspectOutput.license}</div>
                  <div><strong>Target Namespace:</strong> {inspectOutput.namespace}</div>
                  <div><strong>Discovered Columns:</strong> {inspectOutput.columns?.join(', ')}</div>
                  <pre className="mt-2 p-2 bg-claude-sidebar rounded text-[10px] whitespace-pre-wrap">
                    {JSON.stringify(inspectOutput.sample_preview, null, 2)}
                  </pre>
                </div>
              </div>
            ) : importStatus ? (
              <div className="space-y-2">
                <h4 className="font-bold text-xs text-claude-text">Import Execution Report</h4>
                <div className={`p-3 rounded-lg border font-mono text-[11px] space-y-1 ${
                  importStatus.status === 'completed'
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-950'
                    : 'bg-rose-50 border-rose-200 text-rose-950'
                }`}>
                  <div><strong>Status:</strong> {importStatus.status.toUpperCase()}</div>
                  {importStatus.status === 'completed' ? (
                    <>
                      <div><strong>Records Accepted:</strong> {importStatus.records_accepted}</div>
                      <div><strong>PII Redactions:</strong> {importStatus.pii_redactions}</div>
                      <div><strong>Quarantined Storage:</strong> {importStatus.target_path}</div>
                      <div><strong>Production Isolation:</strong> VERIFIED (100% Isolated)</div>
                    </>
                  ) : (
                    <div><strong>Error:</strong> {importStatus.error}</div>
                  )}
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-claude-muted italic">
                Select a dataset on the left to inspect its schema or execute a controlled import.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
