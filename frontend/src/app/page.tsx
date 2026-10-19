'use client'

import React, { useState, useEffect, useRef } from 'react'
import Sidebar from '@/components/Sidebar'
import ChatPane from '@/components/ChatPane'
import SourcePanel from '@/components/SourcePanel'
import MemoryModal from '@/components/MemoryModal'
import TicketModal from '@/components/TicketModal'
import AdminDatasetsModal from '@/components/AdminDatasetsModal'
import {
  ChatSession, ChatMessage, SourceCard, UserProfile,
  fetchUserProfile, switchUserRole, fetchSessions, fetchSessionHistory,
  togglePinSession, streamChatSSE
} from '@/lib/api'

export default function Home() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)

  // Streaming state
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingStatus, setStreamingStatus] = useState<string | null>(null)
  const [streamingDelta, setStreamingDelta] = useState<string>('')
  const [activeSources, setActiveSources] = useState<SourceCard[]>([])
  const [highlightSourceIndex, setHighlightSourceIndex] = useState<number | null>(null)

  // User preferences
  const [selectedLanguage, setSelectedLanguage] = useState('auto')
  const [answerDepth, setAnswerDepth] = useState('standard')

  // Modals
  const [isMemoryOpen, setIsMemoryOpen] = useState(false)
  const [isTicketOpen, setIsTicketOpen] = useState(false)
  const [isDatasetsOpen, setIsDatasetsOpen] = useState(false)
  const [isSourcesOpen, setIsSourcesOpen] = useState(false)
  const [isSidebarOpenMobile, setIsSidebarOpenMobile] = useState(false)
  const [ticketContext, setTicketContext] = useState('')

  const abortControllerRef = useRef<AbortController | null>(null)

  // Initial load
  useEffect(() => {
    loadUserAndSessions()
  }, [])

  const loadUserAndSessions = async () => {
    try {
      const profile = await fetchUserProfile()
      setUserProfile(profile)
      setSelectedLanguage(profile.preferred_language || 'auto')
      setAnswerDepth(profile.answer_depth || 'standard')

      const sessionList = await fetchSessions()
      setSessions(sessionList)
      if (sessionList.length > 0 && !currentSessionId) {
        handleSelectSession(sessionList[0].id)
      }
    } catch (err) {
      console.error('Initialization error:', err)
    }
  }

  const handleSelectSession = async (id: string) => {
    setCurrentSessionId(id)
    try {
      const data = await fetchSessionHistory(id)
      setMessages(data.messages || [])
      // Extract latest sources
      const lastAsst = [...(data.messages || [])].reverse().find(m => m.role === 'assistant')
      if (lastAsst?.sources && lastAsst.sources.length > 0) {
        setActiveSources(lastAsst.sources)
      } else {
        setActiveSources([])
      }
    } catch {
      setMessages([])
    }
  }

  const handleNewChat = () => {
    setCurrentSessionId(null)
    setMessages([])
    setActiveSources([])
    setStreamingDelta('')
    setStreamingStatus(null)
  }

  const handleTogglePin = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const pinned = await togglePinSession(id)
    setSessions(prev => prev.map(s => s.id === id ? { ...s, pinned } : s))
  }

  const handleSwitchRole = async (newRole: string) => {
    try {
      const res = await switchUserRole(newRole)
      setUserProfile(prev => prev ? { ...prev, role: newRole } : null)
      // Refresh current chat under new role scope
      if (currentSessionId) {
        handleSelectSession(currentSessionId)
      }
    } catch (err) {
      console.error('Role switch error:', err)
    }
  }

  const handleSendMessage = async (text: string) => {
    if (isStreaming || !text.trim()) return

    // Optimistically push user message
    const tempUserMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, tempUserMsg])

    setIsStreaming(true)
    setStreamingStatus('Understanding request...')
    setStreamingDelta('')
    abortControllerRef.current = new AbortController()

    let accumulatedDelta = ''

    await streamChatSSE({
      message: text,
      sessionId: currentSessionId || undefined,
      languageOverride: selectedLanguage,
      answerDepth,
      userRole: userProfile?.role,
      onStatus: (msg) => {
        setStreamingStatus(msg)
      },
      onDelta: (delta) => {
        accumulatedDelta += delta
        setStreamingDelta(accumulatedDelta)
      },
      onComplete: (data) => {
        setIsStreaming(false)
        setStreamingStatus(null)

        const asstMsg: ChatMessage = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: accumulatedDelta,
          sources: data.sources || [],
          follow_up_suggestions: data.follow_up_suggestions || [],
          created_at: new Date().toISOString()
        }

        setMessages(prev => [...prev, asstMsg])
        setStreamingDelta('')
        setActiveSources(data.sources || [])

        // If ticket or security incident, suggest ticket opening
        if (text.toLowerCase().includes('phishing') || text.toLowerCase().includes('broken') || text.toLowerCase().includes('stolen')) {
          setTicketContext(text)
        }

        // Refresh session list
        fetchSessions().then(setSessions)
      },
      onError: (err) => {
        setIsStreaming(false)
        setStreamingStatus(null)
        setMessages(prev => [
          ...prev,
          {
            id: `err-${Date.now()}`,
            role: 'assistant',
            content: `**Error:** ${err}. Please check your connection and try again.`,
            created_at: new Date().toISOString()
          }
        ])
      },
      abortSignal: abortControllerRef.current.signal
    })
  }

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsStreaming(false)
      setStreamingStatus(null)
      if (streamingDelta) {
        setMessages(prev => [
          ...prev,
          {
            id: `stopped-${Date.now()}`,
            role: 'assistant',
            content: streamingDelta + ' *(Generation stopped by user)*',
            created_at: new Date().toISOString()
          }
        ])
        setStreamingDelta('')
      }
    }
  }

  const handleRegenerate = () => {
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user')
    if (lastUserMsg) {
      // Drop last assistant response
      setMessages(prev => {
        const idx = prev.findLastIndex(m => m.role === 'assistant')
        if (idx !== -1) return prev.slice(0, idx)
        return prev
      })
      handleSendMessage(lastUserMsg.content)
    }
  }

  const handleOpenSources = (sources: SourceCard[], highlightIdx?: number) => {
    setActiveSources(sources)
    setHighlightSourceIndex(highlightIdx || null)
    setIsSourcesOpen(true)
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-claude-bg">
      {/* Left Sidebar */}
      <Sidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onTogglePin={handleTogglePin}
        userProfile={userProfile}
        onSwitchRole={handleSwitchRole}
        onOpenMemoryModal={() => setIsMemoryOpen(true)}
        onOpenTicketModal={() => { setTicketContext(''); setIsTicketOpen(true); }}
        onOpenDatasetsModal={() => setIsDatasetsOpen(true)}
        selectedLanguage={selectedLanguage}
        onSelectLanguage={setSelectedLanguage}
        answerDepth={answerDepth}
        onSelectAnswerDepth={setAnswerDepth}
        isOpenMobile={isSidebarOpenMobile}
        onCloseMobile={() => setIsSidebarOpenMobile(false)}
      />

      {/* Main Chat Interface */}
      <ChatPane
        messages={messages}
        streamingStatus={streamingStatus}
        streamingDelta={streamingDelta}
        isStreaming={isStreaming}
        onSendMessage={handleSendMessage}
        onStopGeneration={handleStopGeneration}
        onRegenerate={handleRegenerate}
        onOpenSources={handleOpenSources}
        onToggleSidebar={() => setIsSidebarOpenMobile(prev => !prev)}
        activeSources={activeSources}
        userRole={userProfile?.role}
      />

      {/* Expandable Right Source Cards Panel */}
      <SourcePanel
        sources={activeSources}
        isOpen={isSourcesOpen}
        onClose={() => setIsSourcesOpen(false)}
        highlightIndex={highlightSourceIndex}
      />

      {/* Modals */}
      <MemoryModal
        isOpen={isMemoryOpen}
        onClose={() => setIsMemoryOpen(false)}
        currentSessionId={currentSessionId}
        onConversationForgotten={handleNewChat}
      />

      <TicketModal
        isOpen={isTicketOpen}
        onClose={() => setIsTicketOpen(false)}
        initialContext={ticketContext}
      />

      <AdminDatasetsModal
        isOpen={isDatasetsOpen}
        onClose={() => setIsDatasetsOpen(false)}
      />
    </div>
  )
}
