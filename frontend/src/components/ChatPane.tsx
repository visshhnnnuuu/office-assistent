import React, { useState, useRef, useEffect } from 'react'
import {
  Send, Square, Copy, Check, ThumbsUp, ThumbsDown,
  AlertTriangle, RotateCcw, Paperclip, Loader2, Sparkles,
  Bookmark, Menu, MessageSquare
} from 'lucide-react'
import { ChatMessage, SourceCard, submitFeedback } from '@/lib/api'

interface ChatPaneProps {
  messages: ChatMessage[]
  streamingStatus: string | null
  streamingDelta: string
  isStreaming: boolean
  onSendMessage: (text: string) => void
  onStopGeneration: () => void
  onRegenerate: () => void
  onOpenSources: (sources: SourceCard[], highlightIdx?: number) => void
  onToggleSidebar: () => void
  activeSources: SourceCard[]
  userRole?: string
}

export default function ChatPane({
  messages,
  streamingStatus,
  streamingDelta,
  isStreaming,
  onSendMessage,
  onStopGeneration,
  onRegenerate,
  onOpenSources,
  onToggleSidebar,
  activeSources,
  userRole
}: ChatPaneProps) {
  const [inputValue, setInputValue] = useState('')
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [feedbackGiven, setFeedbackGiven] = useState<Record<string, string>>({})
  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, streamingDelta, streamingStatus])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (inputValue.trim() && !isStreaming) {
        onSendMessage(inputValue.trim())
        setInputValue('')
      }
    }
  }

  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleFeedback = async (messageId: string, type: 'helpful' | 'not_helpful' | 'reported') => {
    setFeedbackGiven(prev => ({ ...prev, [messageId]: type }))
    try {
      await submitFeedback(messageId, type)
    } catch {}
  }

  // Helper to parse citations [1], [2] and render clickable pills
  const renderMessageContent = (content: string, sources: SourceCard[] = []) => {
    // Split into paragraphs / code blocks
    const parts = content.split(/(```[\s\S]*?```)/g)

    return parts.map((part, pIdx) => {
      if (part.startsWith('```')) {
        const codeLines = part.slice(3, -3).trim().split('\n')
        const language = codeLines[0].trim() || 'code'
        const codeText = codeLines.slice(1).join('\n')

        return (
          <div key={pIdx} className="my-3 rounded-lg overflow-hidden border border-claude-border bg-[#1E1E1E] text-gray-200 text-xs">
            <div className="flex items-center justify-between px-3 py-1.5 bg-[#2D2D2D] text-gray-400 font-mono text-[11px]">
              <span>{language}</span>
              <button
                onClick={() => handleCopyText(codeText, `code-${pIdx}`)}
                className="hover:text-white flex items-center gap-1"
              >
                {copiedId === `code-${pIdx}` ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                <span>{copiedId === `code-${pIdx}` ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
            <pre className="p-3 overflow-x-auto font-mono text-[11.5px] leading-relaxed">
              <code>{codeText}</code>
            </pre>
          </div>
        )
      }

      // Normal text with heading & citation replacements
      const lines = part.split('\n')
      return (
        <div key={pIdx} className="space-y-1.5">
          {lines.map((line, lIdx) => {
            if (line.startsWith('### ')) {
              return (
                <h3 key={lIdx} className="font-semibold text-sm text-claude-text mt-3 mb-1 text-slate-800">
                  {line.replace('### ', '')}
                </h3>
              )
            }
            if (line.startsWith('## ')) {
              return (
                <h2 key={lIdx} className="font-bold text-sm text-claude-text mt-4 mb-1">
                  {line.replace('## ', '')}
                </h2>
              )
            }
            if (line.startsWith('# ')) {
              return (
                <h1 key={lIdx} className="font-bold text-base text-claude-text mt-4 mb-2">
                  {line.replace('# ', '')}
                </h1>
              )
            }
            if (line.startsWith('- ') || line.startsWith('* ')) {
              return (
                <li key={lIdx} className="ml-4 list-disc text-xs leading-relaxed text-claude-text">
                  {renderLineWithCitations(line.slice(2), sources)}
                </li>
              )
            }
            if (/^\d+\.\s/.test(line)) {
              return (
                <li key={lIdx} className="ml-4 list-decimal text-xs leading-relaxed text-claude-text">
                  {renderLineWithCitations(line.replace(/^\d+\.\s/, ''), sources)}
                </li>
              )
            }
            if (!line.trim()) {
              return <div key={lIdx} className="h-1.5" />
            }

            return (
              <p key={lIdx} className="text-xs leading-relaxed text-claude-text">
                {renderLineWithCitations(line, sources)}
              </p>
            )
          })}
        </div>
      )
    })
  }

  const renderLineWithCitations = (line: string, sources: SourceCard[]) => {
    // Matches markdown citations like [1], [2], [1], [2]
    const tokenRegex = /(\[\d+\])/g
    const segments = line.split(tokenRegex)

    return segments.map((seg, sIdx) => {
      const match = seg.match(/^\[(\d+)\]$/)
      if (match) {
        const citationNum = parseInt(match[1], 10)
        return (
          <button
            key={sIdx}
            onClick={() => onOpenSources(sources, citationNum)}
            className="citation-badge"
            title="Click to view verified source reference"
          >
            {citationNum}
          </button>
        )
      }
      return <span key={sIdx}>{seg}</span>
    })
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-claude-bg overflow-hidden relative">
      {/* Top Navbar */}
      <div className="h-12 border-b border-claude-border flex items-center justify-between px-4 bg-claude-card/60 backdrop-blur-xs shrink-0">
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleSidebar}
            className="md:hidden text-claude-muted hover:text-claude-text p-1"
          >
            <Menu size={18} />
          </button>
          <span className="font-semibold text-xs text-claude-text flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Office Knowledge Assistant</span>
          </span>
          {userRole && (
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-claude-sidebar border border-claude-border text-claude-muted">
              Role: {userRole}
            </span>
          )}
        </div>

        {activeSources.length > 0 && (
          <button
            onClick={() => onOpenSources(activeSources)}
            className="flex items-center gap-1.5 text-xs text-claude-accent font-medium hover:bg-claude-highlight px-2 py-1 rounded transition-colors"
          >
            <Bookmark size={13} />
            <span>{activeSources.length} Sources</span>
          </button>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 md:px-16 lg:px-28 space-y-6">
        {messages.length === 0 && !isStreaming ? (
          <div className="py-16 text-center max-w-md mx-auto space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-claude-highlight text-claude-accent flex items-center justify-center mx-auto shadow-xs">
              <Sparkles size={24} />
            </div>
            <h2 className="text-base font-semibold text-claude-text">
              How can I assist your work today?
            </h2>
            <p className="text-xs text-claude-muted leading-relaxed">
              I can explain company policies, HR benefits, IT troubleshooting SOPs, travel reimbursement workflows, or assist in software development with zero hallucinations.
            </p>

            {/* Quick Starter Prompts */}
            <div className="grid grid-cols-1 gap-2 pt-4 text-left">
              {[
                "How do I apply for travel reimbursement and Form 12BB?",
                "What is the carry-forward limit for casual leave?",
                "Leave apply karne ka full process kya hai?",
                "Leave apply cheyyan entha steps?",
                "How do I fix Cisco AnyConnect VPN Error 401?",
              ].map((starter, sIdx) => (
                <button
                  key={sIdx}
                  onClick={() => onSendMessage(starter)}
                  className="p-2.5 bg-claude-card hover:bg-claude-highlight border border-claude-border hover:border-claude-accent rounded-lg text-xs text-claude-text text-left transition-all shadow-2xs"
                >
                  {starter}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-2xl rounded-xl p-4 text-xs transition-all ${
                  msg.role === 'user'
                    ? 'bg-claude-card border border-claude-border font-medium text-claude-text shadow-2xs'
                    : 'bg-claude-card/90 border border-claude-border prose-claude shadow-xs w-full'
                }`}
              >
                {msg.role === 'user' ? (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <div>
                    {renderMessageContent(msg.content, msg.sources || [])}

                    {/* Sources Badge Pill Bar */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-claude-border/50 flex flex-wrap items-center gap-1.5">
                        <span className="text-[10px] font-semibold text-claude-muted uppercase tracking-wider mr-1">
                          Sources:
                        </span>
                        {msg.sources.map((s) => (
                          <button
                            key={s.citation_index}
                            onClick={() => onOpenSources(msg.sources || [], s.citation_index)}
                            className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-claude-sidebar border border-claude-border hover:border-claude-accent text-claude-text transition-colors"
                          >
                            <span className="w-3.5 h-3.5 rounded-full bg-claude-accent text-white flex items-center justify-center text-[9px] font-bold">
                              {s.citation_index}
                            </span>
                            <span className="truncate max-w-[140px]">{s.title}</span>
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Follow-up Suggestions */}
                    {msg.follow_up_suggestions && msg.follow_up_suggestions.length > 0 && (
                      <div className="mt-3 pt-2 flex flex-wrap gap-1.5">
                        {msg.follow_up_suggestions.map((sug, sIdx) => (
                          <button
                            key={sIdx}
                            onClick={() => onSendMessage(sug)}
                            className="px-2.5 py-1 rounded-full text-[11px] bg-claude-highlight hover:bg-[#EBDDCF] text-claude-accent border border-claude-border font-medium transition-colors"
                          >
                            + {sug}
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Assistant Message Actions */}
                    <div className="mt-3 pt-2 border-t border-claude-border/40 flex items-center justify-between text-claude-muted text-[11px]">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleCopyText(msg.content, msg.id)}
                          className="hover:text-claude-text flex items-center gap-1 transition-colors"
                        >
                          {copiedId === msg.id ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
                          <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                        </button>

                        <button
                          onClick={onRegenerate}
                          className="hover:text-claude-text flex items-center gap-1 transition-colors ml-2"
                        >
                          <RotateCcw size={12} />
                          <span>Regenerate</span>
                        </button>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleFeedback(msg.id, 'helpful')}
                          className={`p-1 rounded hover:text-emerald-600 transition-colors ${
                            feedbackGiven[msg.id] === 'helpful' ? 'text-emerald-600 font-bold' : ''
                          }`}
                          title="Helpful"
                        >
                          <ThumbsUp size={12} />
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, 'not_helpful')}
                          className={`p-1 rounded hover:text-rose-600 transition-colors ${
                            feedbackGiven[msg.id] === 'not_helpful' ? 'text-rose-600 font-bold' : ''
                          }`}
                          title="Not Helpful"
                        >
                          <ThumbsDown size={12} />
                        </button>
                        <button
                          onClick={() => handleFeedback(msg.id, 'reported')}
                          className={`p-1 rounded hover:text-amber-600 transition-colors ${
                            feedbackGiven[msg.id] === 'reported' ? 'text-amber-600 font-bold' : ''
                          }`}
                          title="Report Incorrect Answer"
                        >
                          <AlertTriangle size={12} />
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Live Streaming Delta Bubble */}
        {isStreaming && (
          <div className="flex flex-col items-start w-full">
            <div className="max-w-2xl w-full rounded-xl p-4 bg-claude-card border border-claude-border prose-claude shadow-xs">
              {/* Dynamic Loading State Indicator */}
              {streamingStatus && (
                <div className="flex items-center gap-2 text-xs text-claude-accent font-medium mb-3 bg-claude-highlight px-2.5 py-1.5 rounded-lg border border-claude-border">
                  <Loader2 size={13} className="animate-spin text-claude-accent shrink-0" />
                  <span>{streamingStatus}</span>
                </div>
              )}

              {/* Streaming Content */}
              {streamingDelta ? (
                renderMessageContent(streamingDelta)
              ) : (
                <div className="flex items-center gap-1 text-claude-muted text-xs italic py-2">
                  <span>Thinking...</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Input Message Composer Bar */}
      <div className="p-4 border-t border-claude-border bg-claude-card/80 backdrop-blur-xs shrink-0">
        <div className="max-w-3xl mx-auto relative rounded-xl border border-claude-border bg-claude-card shadow-sm focus-within:border-claude-accent focus-within:ring-1 focus-within:ring-claude-accent transition-all">
          <textarea
            ref={textareaRef}
            rows={2}
            placeholder="Ask about office policies, HR workflows, IT troubleshooting, or software topics..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full px-3.5 pt-3 pb-8 text-xs bg-transparent focus:outline-none resize-none placeholder:text-claude-muted"
          />

          <div className="absolute bottom-2 left-3 right-3 flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-claude-muted">
              <span className="text-[10px] text-claude-muted">
                Press <strong>Enter</strong> to send, <strong>Shift+Enter</strong> for newline
              </span>
            </div>

            <div className="flex items-center gap-2">
              {isStreaming ? (
                <button
                  onClick={onStopGeneration}
                  className="flex items-center gap-1 py-1 px-2.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-medium transition-colors shadow-xs"
                >
                  <Square size={12} />
                  <span>Stop</span>
                </button>
              ) : (
                <button
                  onClick={() => {
                    if (inputValue.trim()) {
                      onSendMessage(inputValue.trim())
                      setInputValue('')
                    }
                  }}
                  disabled={!inputValue.trim()}
                  className="p-1.5 rounded-lg bg-claude-accent hover:bg-claude-accentHover text-white disabled:opacity-30 transition-all shadow-xs"
                  title="Send message"
                >
                  <Send size={14} />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
