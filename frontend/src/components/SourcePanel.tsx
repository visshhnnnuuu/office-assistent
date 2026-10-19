import React, { useState } from 'react'
import {
  FileText, Globe, ExternalLink, Calendar, ChevronDown,
  ChevronUp, ShieldCheck, Tag, Building2, Bookmark
} from 'lucide-react'
import { SourceCard } from '@/lib/api'

interface SourcePanelProps {
  sources: SourceCard[]
  isOpen: boolean
  onClose: () => void
  highlightIndex?: number | null
}

export default function SourcePanel({
  sources,
  isOpen,
  onClose,
  highlightIndex
}: SourcePanelProps) {
  const [expandedCards, setExpandedCards] = useState<Record<number, boolean>>({})

  const toggleExpand = (idx: number) => {
    setExpandedCards(prev => ({ ...prev, [idx]: !prev[idx] }))
  }

  if (!isOpen || sources.length === 0) return null

  return (
    <div className="w-80 md:w-96 border-l border-claude-border bg-claude-sidebar/50 flex flex-col h-full overflow-hidden transition-all duration-200">
      {/* Header */}
      <div className="p-4 border-b border-claude-border flex items-center justify-between bg-claude-card">
        <div className="flex items-center gap-2">
          <Bookmark size={16} className="text-claude-accent" />
          <h2 className="font-semibold text-sm text-claude-text">
            Retrieved Sources ({sources.length})
          </h2>
        </div>
        <button
          onClick={onClose}
          className="text-xs text-claude-muted hover:text-claude-text px-2 py-1 rounded hover:bg-claude-highlight"
        >
          Close
        </button>
      </div>

      {/* Source Cards List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {sources.map((src, i) => {
          const isHighlighted = highlightIndex === src.citation_index
          const isExpanded = expandedCards[src.citation_index] ?? true

          return (
            <div
              key={i}
              className={`rounded-lg border transition-all shadow-sm ${
                isHighlighted
                  ? 'bg-claude-highlight/80 border-claude-accent ring-1 ring-claude-accent'
                  : 'bg-claude-card border-claude-border hover:border-claude-borderDark'
              }`}
            >
              {/* Card Header */}
              <div
                onClick={() => toggleExpand(src.citation_index)}
                className="p-3 cursor-pointer select-none flex items-start justify-between gap-2"
              >
                <div className="flex items-start gap-2 truncate">
                  <span className="w-5 h-5 rounded-full bg-claude-accent text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                    {src.citation_index}
                  </span>
                  <div className="truncate">
                    <h3 className="font-semibold text-xs text-claude-text truncate" title={src.title}>
                      {src.title}
                    </h3>
                    <p className="text-[11px] text-claude-muted truncate">
                      {src.section_title}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1 shrink-0">
                  <span className={`text-[9px] font-semibold uppercase px-1.5 py-0.5 rounded ${
                    src.source_type === 'internal'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}>
                    {src.source_type === 'internal' ? 'Internal RAG' : 'Official Web'}
                  </span>
                  {isExpanded ? <ChevronUp size={14} className="text-claude-muted" /> : <ChevronDown size={14} className="text-claude-muted" />}
                </div>
              </div>

              {/* Expandable Details */}
              {isExpanded && (
                <div className="px-3 pb-3 pt-1 border-t border-claude-border/50 text-xs space-y-2">
                  {/* Metadata Chips */}
                  <div className="flex flex-wrap gap-1.5 text-[10px] text-claude-muted">
                    <span className="flex items-center gap-1 bg-claude-sidebar px-1.5 py-0.5 rounded border border-claude-border">
                      <Building2 size={10} />
                      <span>{src.department}</span>
                    </span>

                    {src.page_number && (
                      <span className="flex items-center gap-1 bg-claude-sidebar px-1.5 py-0.5 rounded border border-claude-border">
                        <FileText size={10} />
                        <span>Page {src.page_number}</span>
                      </span>
                    )}

                    {src.sheet_name && (
                      <span className="flex items-center gap-1 bg-claude-sidebar px-1.5 py-0.5 rounded border border-claude-border">
                        <Tag size={10} />
                        <span>Sheet: {src.sheet_name}</span>
                      </span>
                    )}

                    {src.version && (
                      <span className="bg-claude-sidebar px-1.5 py-0.5 rounded border border-claude-border">
                        v{src.version}
                      </span>
                    )}

                    <span className="flex items-center gap-1 bg-amber-50 text-amber-800 px-1.5 py-0.5 rounded border border-amber-200 font-medium">
                      <ShieldCheck size={10} />
                      <span className="capitalize">{src.classification}</span>
                    </span>
                  </div>

                  {/* Excerpt */}
                  <div className="bg-claude-sidebar/70 rounded p-2 text-[11px] text-claude-text leading-relaxed font-mono whitespace-pre-wrap border border-claude-border/40">
                    "{src.excerpt}"
                  </div>

                  {/* Footer Timestamps and URL */}
                  <div className="flex items-center justify-between text-[10px] text-claude-muted pt-1">
                    <div className="flex items-center gap-1">
                      <Calendar size={10} />
                      <span>
                        {src.last_reviewed_date
                          ? `Reviewed: ${src.last_reviewed_date}`
                          : (src.retrieval_timestamp || 'Active')}
                      </span>
                    </div>

                    {src.source_url && (
                      <a
                        href={src.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="flex items-center gap-0.5 text-claude-accent hover:underline font-medium"
                      >
                        <span>Open Document</span>
                        <ExternalLink size={10} />
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
