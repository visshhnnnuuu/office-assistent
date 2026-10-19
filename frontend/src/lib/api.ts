export interface SourceCard {
  citation_index: number
  title: string
  source_type: 'internal' | 'public_web'
  department: string
  section_title: string
  page_number?: number | null
  slide_number?: number | null
  sheet_name?: string | null
  row_reference?: string | null
  version?: string | null
  last_reviewed_date?: string | null
  retrieval_timestamp?: string | null
  source_url?: string | null
  excerpt: string
  classification: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  language?: string
  sources?: SourceCard[]
  follow_up_suggestions?: string[]
  feedback?: string | null
  created_at?: string
}

export interface ChatSession {
  id: string
  title: string
  pinned: boolean
  updated_at?: string
  message_count?: number
}

export interface UserProfile {
  id: string
  email: string
  name: string
  role: string
  department: string
  preferred_language: string
  answer_depth: string
  available_roles: string[]
}

export interface UserMemory {
  memory_id: string
  fact: string
  memory_type: string
  sensitivity: string
  created_at?: string
}

export interface ITTicket {
  ticket_number: string
  category: string
  summary: string
  description?: string
  priority: string
  status: string
  assigned_team: string
  created_at?: string
}

export interface DatasetItem {
  name: string
  category: string
  purpose: string
  namespace: string
  dataset_card_url?: string
  license: string
  languages: string[]
  splits: string[]
  enabled: boolean
  description: string
  status_note?: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export async function fetchUserProfile(roleHeader?: string): Promise<UserProfile> {
  const headers: HeadersInit = {}
  if (roleHeader) {
    headers['X-User-Role'] = roleHeader
  }
  const res = await fetch(`${API_BASE}/api/auth/me`, { headers })
  if (!res.ok) throw new Error('Failed to load user profile')
  return res.json()
}

export async function switchUserRole(role: string, department: string = 'All'): Promise<any> {
  const res = await fetch(`${API_BASE}/api/auth/switch-role`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, department }),
  })
  if (!res.ok) throw new Error('Failed to switch role')
  return res.json()
}

export async function fetchSessions(): Promise<ChatSession[]> {
  const res = await fetch(`${API_BASE}/api/chat/sessions`)
  if (!res.ok) return []
  return res.json()
}

export async function fetchSessionHistory(sessionId: string): Promise<{ id: string; title: string; messages: ChatMessage[] }> {
  const res = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}`)
  if (!res.ok) throw new Error('Failed to load conversation history')
  return res.json()
}

export async function togglePinSession(sessionId: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}/pin`, { method: 'POST' })
  if (!res.ok) return false
  const data = await res.json()
  return data.pinned
}

export async function submitFeedback(messageId: string, feedback: string, notes?: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/chat/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message_id: messageId, feedback, notes }),
  })
  return res.json()
}

export async function fetchMemories(): Promise<UserMemory[]> {
  const res = await fetch(`${API_BASE}/api/memory`)
  if (!res.ok) return []
  return res.json()
}

export async function addMemory(fact: string, consent: boolean = true): Promise<any> {
  const res = await fetch(`${API_BASE}/api/memory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fact, consent }),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Failed to save memory')
  }
  return res.json()
}

export async function deleteMemory(memoryId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/memory/${memoryId}`, { method: 'DELETE' })
  return res.json()
}

export async function deleteAllMemories(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/memory`, { method: 'DELETE' })
  return res.json()
}

export async function forgetConversation(sessionId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/memory/forget-conversation/${sessionId}`, { method: 'POST' })
  return res.json()
}

export async function classifyTicketIntent(text: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/tickets/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  return res.json()
}

export async function createTicket(ticketData: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/tickets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ticketData),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Failed to create ticket')
  }
  return res.json()
}

export async function fetchUserTickets(): Promise<ITTicket[]> {
  const res = await fetch(`${API_BASE}/api/tickets`)
  if (!res.ok) return []
  return res.json()
}

export async function listDatasets(): Promise<DatasetItem[]> {
  const res = await fetch(`${API_BASE}/api/datasets`)
  if (!res.ok) return []
  return res.json()
}

export async function inspectDataset(name: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/datasets/inspect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_name: name }),
  })
  return res.json()
}

export async function importDataset(name: string, acceptLicense: boolean, maxRecords: number = 100): Promise<any> {
  const res = await fetch(`${API_BASE}/api/datasets/import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_name: name, accept_license: acceptLicense, max_records: maxRecords }),
  })
  return res.json()
}

export async function streamChatSSE({
  message,
  sessionId,
  languageOverride,
  answerDepth,
  userRole,
  onStatus,
  onDelta,
  onComplete,
  onError,
  abortSignal,
}: {
  message: string
  sessionId?: string
  languageOverride?: string
  answerDepth?: string
  userRole?: string
  onStatus: (msg: string) => void
  onDelta: (delta: string) => void
  onComplete: (data: { sources: SourceCard[]; follow_up_suggestions: string[] }) => void
  onError: (err: string) => void
  abortSignal?: AbortSignal
}) {
  try {
    const headers: HeadersInit = { 'Content-Type': 'application/json' }
    if (userRole) {
      headers['X-User-Role'] = userRole
    }

    const res = await fetch(`${API_BASE}/api/chat/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message,
        session_id: sessionId,
        language_override: languageOverride,
        answer_depth: answerDepth,
      }),
      signal: abortSignal,
    })

    if (!res.ok || !res.body) {
      throw new Error(`Server returned status ${res.status}`)
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const block of lines) {
        if (!block.trim()) continue
        const eventMatch = block.match(/event:\s*([^\n]+)/)
        const dataMatch = block.match(/data:\s*([^\n]+)/)

        const event = eventMatch ? eventMatch[1].trim() : 'message'
        const rawData = dataMatch ? dataMatch[1].trim() : ''

        if (event === 'status') {
          try {
            const parsed = JSON.parse(rawData)
            onStatus(parsed.message)
          } catch {}
        } else if (event === 'delta') {
          try {
            const parsed = JSON.parse(rawData)
            onDelta(parsed.delta)
          } catch {}
        } else if (event === 'complete') {
          try {
            const parsed = JSON.parse(rawData)
            onComplete(parsed)
          } catch {}
        }
      }
    }
  } catch (err: any) {
    if (err.name !== 'AbortError') {
      onError(err.message || 'Error communicating with assistant')
    }
  }
}
