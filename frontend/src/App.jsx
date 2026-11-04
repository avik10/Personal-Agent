import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatArea from './components/ChatArea';
import InputBar from './components/InputBar';
import GoogleHub from './features/google/GoogleHub';
import GoogleConnectModal from './features/google/GoogleConnectModal';
import MicrosoftHub from './features/microsoft/MicrosoftHub';
import { API_BASE, getApiUrl } from './config/api';

export default function App() {
  const [activeView, setActiveView] = useState('chat'); // 'chat' | 'google' | 'microsoft'
  const [activeGoogleTab, setActiveGoogleTab] = useState('gmail'); // 'gmail' | 'calendar' | 'drive' | 'notes'
  const [activeMicrosoftTab, setActiveMicrosoftTab] = useState('outlook'); // 'outlook'
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [agentsList, setAgentsList] = useState([]);
  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem('personal_agent_chats');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        // fallback
      }
    }
    return [
      {
        id: 'chat-default',
        title: 'New Conversation',
        createdAt: new Date().toISOString(),
        messages: [],
      },
    ];
  });
  const [currentChatId, setCurrentChatId] = useState(() => chats[0]?.id || 'chat-default');
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Sync chats to localStorage
  useEffect(() => {
    localStorage.setItem('personal_agent_chats', JSON.stringify(chats));
  }, [chats]);

  const loadStatus = async () => {
    try {
      const res = await fetch(getApiUrl('/api/status'));
      if (res.ok) {
        const data = await res.json();
        setSystemStatus(data);
      }
    } catch (err) {
      console.warn('API server is not reachable yet at', API_BASE || window.location.origin);
    }

    try {
      const resAgents = await fetch(getApiUrl('/api/agents'));
      if (resAgents.ok) {
        const dataAgents = await resAgents.json();
        setAgentsList(dataAgents.agents || []);
      }
    } catch (err) {
      // silent
    }
  };

  // Fetch system status and agent roster on load
  useEffect(() => {
    loadStatus();
    const interval = setInterval(loadStatus, 15000);

    // Detect OAuth callback redirects from Google or Microsoft
    const params = new URLSearchParams(window.location.search);
    if (params.get('microsoft_auth') === 'success') {
      setActiveView('microsoft');
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (params.get('google_auth') === 'success') {
      setActiveView('google');
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (activeView === 'chat') {
      scrollToBottom();
    }
  }, [chats, isLoading, activeView]);

  const currentChat = chats.find((c) => c.id === currentChatId) || chats[0];

  const handleNewChat = () => {
    const newChat = {
      id: `chat-${Date.now()}`,
      title: 'New Conversation',
      createdAt: new Date().toISOString(),
      messages: [],
    };
    setChats((prev) => [newChat, ...prev]);
    setCurrentChatId(newChat.id);
  };

  const handleDeleteChat = (id) => {
    if (chats.length <= 1) {
      handleNewChat();
      return;
    }
    const updated = chats.filter((c) => c.id !== id);
    setChats(updated);
    if (currentChatId === id) {
      setCurrentChatId(updated[0].id);
    }
  };

  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || input).trim();
    if (!query || isLoading) return;

    setInput('');

    // Append user message
    const userMsg = { role: 'user', content: query, timestamp: new Date().toISOString() };
    const updatedMessages = [...(currentChat?.messages || []), userMsg];

    // Set first message as chat title if it's new
    let updatedTitle = currentChat?.title;
    if (currentChat?.title === 'New Conversation' || !currentChat?.messages.length) {
      updatedTitle = query.slice(0, 32) + (query.length > 32 ? '...' : '');
    }

    setChats((prev) =>
      prev.map((c) =>
        c.id === currentChatId
          ? { ...c, title: updatedTitle, messages: updatedMessages }
          : c
      )
    );

    setIsLoading(true);

    try {
      const response = await fetch(getApiUrl('/api/chat'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      const data = await response.json();

      const assistantMsg = {
        role: 'assistant',
        content: data.response || 'Action completed.',
        active_agents: data.active_agents || [],
        agent_outputs: data.agent_outputs || {},
        timestamp: new Date().toISOString(),
      };

      setChats((prev) =>
        prev.map((c) =>
          c.id === currentChatId
            ? { ...c, messages: [...updatedMessages, assistantMsg] }
            : c
        )
      );
    } catch (err) {
      const errorMsg = {
        role: 'assistant',
        content: `⚠️ Failed to get response from agent: ${err.message}. Please make sure the backend API server is running on http://localhost:8000.`,
        active_agents: ['error'],
        agent_outputs: {},
        timestamp: new Date().toISOString(),
      };

      setChats((prev) =>
        prev.map((c) =>
          c.id === currentChatId
            ? { ...c, messages: [...updatedMessages, errorMsg] }
            : c
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleAskAgentFromGoogle = (prompt) => {
    setActiveView('chat');
    handleSendMessage(prompt);
  };

  const handleAskAgentFromMicrosoft = (prompt) => {
    setActiveView('chat');
    handleSendMessage(prompt);
  };

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeView={activeView}
        setActiveView={setActiveView}
        activeGoogleTab={activeGoogleTab}
        setActiveGoogleTab={setActiveGoogleTab}
        activeMicrosoftTab={activeMicrosoftTab}
        setActiveMicrosoftTab={setActiveMicrosoftTab}
        onOpenConnectModal={() => setIsConnectModalOpen(true)}
        systemStatus={systemStatus}
        agentsList={agentsList}
        chats={chats}
        currentChatId={currentChatId}
        onSelectChat={(id) => {
          setCurrentChatId(id);
          setSidebarOpen(false);
        }}
        onNewChat={() => {
          handleNewChat();
          setSidebarOpen(false);
        }}
        onDeleteChat={handleDeleteChat}
      />

      {/* Main Workspace Canvas */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          background: 'var(--bg-primary)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Header
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          systemStatus={systemStatus}
          activeView={activeView}
          setActiveView={setActiveView}
          onOpenConnectModal={() => setIsConnectModalOpen(true)}
        />

        {/* Dynamic View: Chat Studio vs Google Workspace Bucket vs Microsoft Bucket */}
        {activeView === 'chat' ? (
          <>
            <ChatArea
              messages={currentChat?.messages || []}
              isLoading={isLoading}
              onSelectPrompt={handleSendMessage}
              onNavigateGoogle={() => setActiveView('google')}
              messagesEndRef={messagesEndRef}
            />

            <InputBar
              input={input}
              setInput={setInput}
              onSendMessage={handleSendMessage}
              onNavigateGoogle={() => setActiveView('google')}
              isLoading={isLoading}
            />
          </>
        ) : activeView === 'google' ? (
          <GoogleHub
            systemStatus={systemStatus}
            onRefreshStatus={loadStatus}
            onAskAgent={handleAskAgentFromGoogle}
            onNavigateChat={() => setActiveView('chat')}
            activeTab={activeGoogleTab}
            setActiveTab={setActiveGoogleTab}
          />
        ) : (
          <MicrosoftHub
            systemStatus={systemStatus}
            onRefreshStatus={loadStatus}
            onAskAgent={handleAskAgentFromMicrosoft}
            onNavigateChat={() => setActiveView('chat')}
            activeTab={activeMicrosoftTab}
            setActiveTab={setActiveMicrosoftTab}
          />
        )}
      </div>

      {/* Global Google Connect Modal */}
      <GoogleConnectModal
        isOpen={isConnectModalOpen}
        onClose={() => setIsConnectModalOpen(false)}
        systemStatus={systemStatus}
        onRefreshStatus={loadStatus}
      />
    </div>
  );
}
