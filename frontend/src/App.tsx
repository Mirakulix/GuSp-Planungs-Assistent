import { useState } from 'react'
import './App.css'

// Note: Mantine components will be imported once dependencies are installed
// import { MantineProvider, AppShell, Title, Container } from '@mantine/core'
// import { Notifications } from '@mantine/notifications'
// import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock imports for now
const MantineProvider = ({ children }: { children: React.ReactNode }) => <div>{children}</div>
const AppShell = ({ children }: { children: React.ReactNode }) => <div>{children}</div>
const Container = ({ children }: { children: React.ReactNode }) => <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1rem' }}>{children}</div>
const Title = ({ children }: { children: React.ReactNode }) => <h1>{children}</h1>

// Components (will be separated into individual files)
const ChatInterface = () => {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([])

  const sendMessage = async () => {
    if (!message.trim()) return

    // Add user message
    const newMessages = [...messages, { role: 'user', content: message }]
    setMessages(newMessages)

    try {
      // Mock API call for now
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessages([...newMessages, { role: 'assistant', content: data.message }])
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages([...newMessages, { role: 'assistant', content: 'Entschuldigung, es gab einen Fehler. Bitte versuche es später erneut.' }])
    }

    setMessage('')
  }

  return (
    <div style={{ maxWidth: '800px', margin: '2rem auto', border: '1px solid #ddd', borderRadius: '8px', padding: '1rem' }}>
      <h2>💬 Pfadi AI Assistent</h2>
      <div style={{ height: '400px', overflowY: 'auto', border: '1px solid #eee', padding: '1rem', marginBottom: '1rem' }}>
        {messages.length === 0 ? (
          <p style={{ color: '#666', textAlign: 'center' }}>
            Hallo! Ich bin dein Pfadi AI Assistent. Wie kann ich dir bei der Planung helfen? 🏕️
          </p>
        ) : (
          messages.map((msg, index) => (
            <div key={index} style={{ 
              marginBottom: '1rem', 
              padding: '0.5rem',
              backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5',
              borderRadius: '4px'
            }}>
              <strong>{msg.role === 'user' ? '🧑‍💼 Du:' : '🤖 Assistent:'}</strong>
              <p style={{ margin: '0.5rem 0 0 0' }}>{msg.content}</p>
            </div>
          ))
        )}
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Frag mich nach Spielen, Heimstunden oder Pfadfinderwissen..."
          style={{ 
            flex: 1, 
            padding: '0.5rem', 
            border: '1px solid #ddd', 
            borderRadius: '4px' 
          }}
        />
        <button 
          onClick={sendMessage}
          style={{ 
            padding: '0.5rem 1rem', 
            backgroundColor: '#1976d2', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Senden
        </button>
      </div>
    </div>
  )
}

const GameSearch = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [games, setGames] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const searchGames = async () => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await fetch(`/api/v1/games/search?q=${encodeURIComponent(searchQuery)}`)
      if (response.ok) {
        const data = await response.json()
        setGames(data.games)
      }
    } catch (error) {
      console.error('Search error:', error)
    }
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: '800px', margin: '2rem auto' }}>
      <h2>🎯 Spiele suchen</h2>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && searchGames()}
          placeholder="Suche nach Spielen..."
          style={{ 
            flex: 1, 
            padding: '0.5rem', 
            border: '1px solid #ddd', 
            borderRadius: '4px' 
          }}
        />
        <button 
          onClick={searchGames}
          disabled={loading}
          style={{ 
            padding: '0.5rem 1rem', 
            backgroundColor: '#1976d2', 
            color: 'white', 
            border: 'none', 
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {loading ? 'Suche...' : 'Suchen'}
        </button>
      </div>
      
      <div>
        {games.map((game, index) => (
          <div key={index} style={{ 
            border: '1px solid #ddd', 
            borderRadius: '8px', 
            padding: '1rem', 
            marginBottom: '1rem' 
          }}>
            <h3>{game.name}</h3>
            <p>{game.description}</p>
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.9rem', color: '#666' }}>
              <span>⏱️ {game.durationMinutes} Min</span>
              <span>👥 {game.minParticipants}-{game.maxParticipants} Personen</span>
              <span>📍 {game.location === 'both' ? 'Drinnen & Draußen' : game.location === 'indoor' ? 'Drinnen' : 'Draußen'}</span>
            </div>
            {game.tags && (
              <div style={{ marginTop: '0.5rem' }}>
                {game.tags.map((tag: string, tagIndex: number) => (
                  <span key={tagIndex} style={{ 
                    backgroundColor: '#e1f5fe', 
                    padding: '0.2rem 0.5rem', 
                    borderRadius: '12px', 
                    fontSize: '0.8rem',
                    marginRight: '0.5rem'
                  }}>
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function App() {
  const [activeTab, setActiveTab] = useState('chat')

  return (
    <MantineProvider>
      <AppShell>
        <Container>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <Title>
              🏕️ Pfadi AI Assistent
            </Title>
          </div>
          
          <nav style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            gap: '1rem', 
            marginBottom: '2rem' 
          }}>
            <button 
              onClick={() => setActiveTab('chat')}
              style={{ 
                padding: '0.5rem 1rem',
                backgroundColor: activeTab === 'chat' ? '#1976d2' : '#f5f5f5',
                color: activeTab === 'chat' ? 'white' : 'black',
                border: '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              💬 Chat
            </button>
            <button 
              onClick={() => setActiveTab('games')}
              style={{ 
                padding: '0.5rem 1rem',
                backgroundColor: activeTab === 'games' ? '#1976d2' : '#f5f5f5',
                color: activeTab === 'games' ? 'white' : 'black',
                border: '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              🎯 Spiele
            </button>
            <button 
              onClick={() => setActiveTab('planning')}
              style={{ 
                padding: '0.5rem 1rem',
                backgroundColor: activeTab === 'planning' ? '#1976d2' : '#f5f5f5',
                color: activeTab === 'planning' ? 'white' : 'black',
                border: '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              📅 Planung
            </button>
          </nav>

          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'games' && <GameSearch />}
          {activeTab === 'planning' && (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <h2>📅 Heimstunden-Planung</h2>
              <p>Coming soon... 🚧</p>
            </div>
          )}
        </Container>
      </AppShell>
    </MantineProvider>
  )
}

export default App