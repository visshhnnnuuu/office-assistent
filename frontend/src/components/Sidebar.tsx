import React, { useState } from 'react'
import {
  Plus, Search, Pin, MessageSquare, Shield,
  Brain, Globe, Settings, Database, Ticket, ChevronRight, X
} from 'lucide-react'
import { ChatSession, UserProfile } from '@/lib/api'

interface SidebarProps {
  sessions: ChatSession[]
  currentSessionId: string | null
  onSelectSession: (id: string) => void
  onNewChat: () => void
  onTogglePin: (id: string, e: React.MouseEvent) => void
  userProfile: UserProfile | null
  onSwitchRole: (role: string) => void
  onOpenMemoryModal: () => void
  onOpenTicketModal: () => void
  onOpenDatasetsModal: () => void
  selectedLanguage: string
  onSelectLanguage: (lang: string) => void
  answerDepth: string
  onSelectAnswerDepth: (depth: string) => void
  isOpenMobile: boolean
  onCloseMobile: () => void
}

export const LANGUAGE_OPTIONS = [
  { id: 'auto', label: 'Auto Detect' },
  { id: 'eng_Latn', label: 'English' },
  { id: 'hin_Deva', label: 'हिंदी (Hindi)' },
  { id: 'hin_Latn', label: 'Hinglish (Romanized)' },
  { id: 'mal_Mlym', label: 'മലയാളം (Malayalam)' },
  { id: 'mal_Latn', label: 'Manglish (Romanized)' },
]

export const ANSWER_DEPTHS = [
  { id: 'concise', label: 'Concise' },
  { id: 'standard', label: 'Standard' },
  { id: 'detailed', label: 'Detailed' },
]

export default function Sidebar({
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onTogglePin,
  userProfile,
  onSwitchRole,
  onOpenMemoryModal,
  onOpenTicketModal,
  onOpenDatasetsModal,
  selectedLanguage,
  onSelectLanguage,
  answerDepth,
  onSelectAnswerDepth,
  isOpenMobile,
  onCloseMobile
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('')

  const filteredSessions = sessions.filter(s =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const pinnedSessions = filteredSessions.filter(s => s.pinned)
  const recentSessions = filteredSessions.filter(s => !s.pinned)

  const isAdminRole = userProfile && ['system_admin', 'it_admin'].includes(userProfile.role)

  return (
    <>
      {/* Mobile backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 bg-black/30 z-40 md:hidden"
          onClick={onCloseMobile}
        />
      )}

      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-72 bg-claude-sidebar border-r border-claude-border flex flex-col justify-between
        transition-transform duration-200 ease-in-out
        ${isOpenMobile ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Header & New Chat */}
        <div className="p-4 border-b border-claude-border">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-claude-accent text-white flex items-center justify-center font-bold text-sm shadow-sm">
                OA
              </div>
              <div>
                <h1 className="font-semibold text-sm leading-tight text-claude-text">
                  Office Assistant
                </h1>
                <span className="text-[11px] text-claude-muted font-medium">Enterprise Copilot</span>
              </div>
            </div>
            <button
              onClick={onCloseMobile}
              className="md:hidden text-claude-muted hover:text-claude-text p-1"
            >
              <X size={18} />
            </button>
          </div>

          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-claude-card hover:bg-white text-claude-text border border-claude-border rounded-lg text-sm font-medium shadow-sm transition-all hover:border-claude-borderDark"
          >
            <Plus size={16} className="text-claude-accent" />
            <span>New Chat</span>
          </button>

          {/* Search Box */}
          <div className="mt-3 relative">
            <Search size={14} className="absolute left-2.5 top-2.5 text-claude-muted" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-claude-card/70 border border-claude-border rounded-md text-xs placeholder:text-claude-muted focus:outline-none focus:border-claude-accent"
            />
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-4">
          {/* Pinned Chats */}
          {pinnedSessions.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 px-2 py-1 text-[11px] font-semibold text-claude-muted uppercase tracking-wider">
                <Pin size={11} className="text-claude-accent" />
                <span>Pinned</span>
              </div>
              <div className="space-y-0.5 mt-1">
                {pinnedSessions.map(session => (
                  <div
                    key={session.id}
                    onClick={() => { onSelectSession(session.id); onCloseMobile(); }}
                    className={`group flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs cursor-pointer transition-colors ${
                      currentSessionId === session.id
                        ? 'bg-claude-highlight font-semibold text-claude-text border border-claude-border'
                        : 'text-claude-muted hover:bg-claude-card hover:text-claude-text'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <MessageSquare size={13} className="shrink-0 text-claude-accent" />
                      <span className="truncate">{session.title}</span>
                    </div>
                    <button
                      onClick={(e) => onTogglePin(session.id, e)}
                      className="opacity-0 group-hover:opacity-100 text-claude-muted hover:text-claude-accent p-0.5"
                    >
                      <Pin size={12} className="fill-current" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Chats */}
          <div>
            <div className="px-2 py-1 text-[11px] font-semibold text-claude-muted uppercase tracking-wider">
              <span>Recent Conversations</span>
            </div>
            <div className="space-y-0.5 mt-1">
              {recentSessions.length === 0 ? (
                <div className="px-2.5 py-3 text-xs text-claude-muted italic">
                  No conversations found
                </div>
              ) : (
                recentSessions.map(session => (
                  <div
                    key={session.id}
                    onClick={() => { onSelectSession(session.id); onCloseMobile(); }}
                    className={`group flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs cursor-pointer transition-colors ${
                      currentSessionId === session.id
                        ? 'bg-claude-highlight font-semibold text-claude-text border border-claude-border'
                        : 'text-claude-muted hover:bg-claude-card hover:text-claude-text'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <MessageSquare size={13} className="shrink-0" />
                      <span className="truncate">{session.title}</span>
                    </div>
                    <button
                      onClick={(e) => onTogglePin(session.id, e)}
                      className="opacity-0 group-hover:opacity-100 text-claude-muted hover:text-claude-accent p-0.5"
                    >
                      <Pin size={12} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Footer: User Profile, Preferences & Tools */}
        <div className="p-3 border-t border-claude-border bg-claude-sidebar/80 space-y-2">
          {/* Language Selector */}
          <div className="flex items-center justify-between text-xs px-1">
            <span className="flex items-center gap-1.5 text-claude-muted font-medium">
              <Globe size={13} />
              <span>Language:</span>
            </span>
            <select
              value={selectedLanguage}
              onChange={(e) => onSelectLanguage(e.target.value)}
              className="bg-claude-card border border-claude-border rounded px-1.5 py-0.5 text-xs text-claude-text focus:outline-none focus:border-claude-accent"
            >
              {LANGUAGE_OPTIONS.map(opt => (
                <option key={opt.id} value={opt.id}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* Answer Depth */}
          <div className="flex items-center justify-between text-xs px-1">
            <span className="text-claude-muted font-medium">Depth:</span>
            <div className="flex gap-1">
              {ANSWER_DEPTHS.map(d => (
                <button
                  key={d.id}
                  onClick={() => onSelectAnswerDepth(d.id)}
                  className={`px-1.5 py-0.5 text-[10px] rounded font-medium ${
                    answerDepth === d.id
                      ? 'bg-claude-accent text-white'
                      : 'bg-claude-card text-claude-muted border border-claude-border hover:text-claude-text'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Action Buttons: Memory & IT Ticket */}
          <div className="grid grid-cols-2 gap-1.5 pt-1">
            <button
              onClick={onOpenMemoryModal}
              className="flex items-center justify-center gap-1.5 py-1.5 px-2 bg-claude-card hover:bg-white text-claude-text border border-claude-border rounded text-xs font-medium transition-colors"
            >
              <Brain size={13} className="text-claude-accent" />
              <span>Memory</span>
            </button>
            <button
              onClick={onOpenTicketModal}
              className="flex items-center justify-center gap-1.5 py-1.5 px-2 bg-claude-card hover:bg-white text-claude-text border border-claude-border rounded text-xs font-medium transition-colors"
            >
              <Ticket size={13} className="text-blue-600" />
              <span>IT Support</span>
            </button>
          </div>

          {/* Admin Dataset Registry Portal Button */}
          {isAdminRole && (
            <button
              onClick={onOpenDatasetsModal}
              className="w-full flex items-center justify-between py-1 px-2 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 rounded text-xs font-medium transition-colors"
            >
              <div className="flex items-center gap-1.5">
                <Database size={13} className="text-purple-600" />
                <span>Dataset Governance</span>
              </div>
              <ChevronRight size={13} />
            </button>
          )}

          {/* User Profile & Role Switcher */}
          {userProfile && (
            <div className="pt-2 border-t border-claude-border/60">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 truncate">
                  <div className="w-6 h-6 rounded-full bg-claude-borderDark flex items-center justify-center text-[10px] font-bold text-claude-text">
                    {userProfile.name.charAt(0)}
                  </div>
                  <div className="truncate">
                    <p className="text-xs font-semibold text-claude-text truncate">{userProfile.name}</p>
                    <p className="text-[10px] text-claude-muted truncate">{userProfile.department}</p>
                  </div>
                </div>

                {/* Role Switcher Pill for Local Testing */}
                <select
                  value={userProfile.role}
                  onChange={(e) => onSwitchRole(e.target.value)}
                  className="text-[11px] font-semibold bg-claude-card border border-claude-border rounded px-1.5 py-0.5 text-claude-accent cursor-pointer hover:border-claude-accent focus:outline-none"
                  title="Switch RBAC Role"
                >
                  {userProfile.available_roles.map(r => (
                    <option key={r} value={r}>{r.toUpperCase()}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>
      </aside>
    </>
  )
}
