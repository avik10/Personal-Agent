import React, { useState } from 'react';
import {
  Plus,
  MessageSquare,
  Mail,
  Calendar,
  HardDrive,
  Bot,
  ChevronDown,
  ChevronUp,
  Cpu,
  Trash2,
  Folder,
  FolderOpen,
  Sparkles,
  CloudSun,
  CheckSquare,
  Calculator,
  ChevronRight,
  Info
} from 'lucide-react';

export default function Sidebar({
  isOpen,
  onClose,
  activeView,
  setActiveView,
  setActiveGoogleTab,
  chats,
  currentChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat
}) {
  const [googleFolderExpanded, setGoogleFolderExpanded] = useState(true);
  const [capabilitiesExpanded, setCapabilitiesExpanded] = useState(true);

  const handleSelectGoogleTab = (tab) => {
    setActiveView('google');
    if (setActiveGoogleTab) setActiveGoogleTab(tab);
    if (onClose) onClose();
  };

  const mcpCapabilities = [
    {
      name: 'Gmail MCP',
      tag: 'Google Workspace',
      desc: 'Live inbox search, unread checks, draft & send emails',
      icon: <Mail size={13} color="#f87171" />,
      color: '#f87171',
      bg: 'rgba(239, 68, 68, 0.1)',
    },
    {
      name: 'Calendar MCP',
      tag: 'Google Workspace',
      desc: 'Agenda inspection, event scheduling & Google Meet',
      icon: <Calendar size={13} color="#60a5fa" />,
      color: '#60a5fa',
      bg: 'rgba(59, 130, 246, 0.1)',
    },
    {
      name: 'Drive MCP',
      tag: 'Google Workspace',
      desc: 'File search, auto-export Docs, spreadsheet parsing',
      icon: <HardDrive size={13} color="#34d399" />,
      color: '#34d399',
      bg: 'rgba(52, 211, 153, 0.1)',
    },
    {
      name: 'Weather MCP',
      tag: 'External API',
      desc: 'Real-time meteorological conditions & 5-day forecasts',
      icon: <CloudSun size={13} color="#fbbf24" />,
      color: '#fbbf24',
      bg: 'rgba(251, 191, 36, 0.1)',
    },
    {
      name: 'Tasks & Notes',
      tag: 'Local Specialist',
      desc: 'Structured to-dos, local notes & scheduled reminders',
      icon: <CheckSquare size={13} color="#a855f7" />,
      color: '#a855f7',
      bg: 'rgba(168, 85, 247, 0.1)',
    },
    {
      name: 'Utility & Math',
      tag: 'Local Specialist',
      desc: 'Financial formulas, unit conversions & system metrics',
      icon: <Calculator size={13} color="#38bdf8" />,
      color: '#38bdf8',
      bg: 'rgba(56, 189, 248, 0.1)',
    },
    {
      name: 'Multi-Agent Supervisor',
      tag: '12 Specialists',
      desc: 'Intent routing, parallel execution & unified synthesis',
      icon: <Sparkles size={13} color="#c084fc" />,
      color: '#c084fc',
      bg: 'rgba(192, 132, 252, 0.1)',
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="mobile-backdrop"
          onClick={onClose}
        />
      )}

      <aside
        className={`app-sidebar ${isOpen ? 'open' : ''}`}
      >
        {/* Top Header & New Chat Button */}
        <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #a855f7 0%, #3b82f6 50%, #ec4899 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 12px rgba(168, 85, 247, 0.35)',
                }}
              >
                <Bot size={18} color="#fff" />
              </div>
              <div>
                <h1 style={{ fontSize: '15px', fontWeight: 700, color: '#f3f4f6', letterSpacing: '-0.02em' }}>
                  Personal Studio
                </h1>
                <p style={{ fontSize: '11px', color: '#9ca3af' }}>Multi-Agent MCP</p>
              </div>
            </div>
          </div>

          {/* New Chat Button */}
          <button
            onClick={() => {
              setActiveView('chat');
              onNewChat();
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              width: '100%',
              padding: '10px 14px',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#f3f4f6',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.09)';
              e.currentTarget.style.borderColor = 'rgba(168, 85, 247, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            }}
          >
            <Plus size={16} color="#a855f7" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Workspaces Navigation */}
        <div style={{ padding: '0 12px 8px 12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div style={{ padding: '4px 6px', fontSize: '10px', fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Workspaces
          </div>

          {/* 1. Chat Studio */}
          <div
            onClick={() => {
              setActiveView('chat');
              if (onClose) onClose();
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 12px',
              borderRadius: '10px',
              background: activeView === 'chat' ? 'rgba(168, 85, 247, 0.14)' : 'transparent',
              border: activeView === 'chat' ? '1px solid rgba(168, 85, 247, 0.3)' : '1px solid transparent',
              color: activeView === 'chat' ? '#f3f4f6' : '#9ca3af',
              fontSize: '13px',
              fontWeight: activeView === 'chat' ? 600 : 500,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
            onMouseEnter={(e) => {
              if (activeView !== 'chat') e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
            }}
            onMouseLeave={(e) => {
              if (activeView !== 'chat') e.currentTarget.style.background = 'transparent';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={15} color={activeView === 'chat' ? '#c084fc' : '#9ca3af'} />
              <span>Chat Studio</span>
            </div>
          </div>

          {/* 2. Google Workspace Bucket Folder */}
          <div
            style={{
              borderRadius: '10px',
              background: activeView === 'google' ? 'rgba(66, 133, 244, 0.1)' : 'transparent',
              border: activeView === 'google' ? '1px solid rgba(66, 133, 244, 0.25)' : '1px solid transparent',
              overflow: 'hidden',
              transition: 'all 0.15s',
            }}
          >
            <div
              onClick={() => {
                setActiveView('google');
                if (onClose) onClose();
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '8px 12px',
                cursor: 'pointer',
                color: activeView === 'google' ? '#f3f4f6' : '#d1d5db',
                fontSize: '13px',
                fontWeight: activeView === 'google' ? 600 : 500,
              }}
              onMouseEnter={(e) => {
                if (activeView !== 'google') e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
              }}
              onMouseLeave={(e) => {
                if (activeView !== 'google') e.currentTarget.style.background = 'transparent';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {googleFolderExpanded ? (
                  <FolderOpen size={15} color="#4285f4" />
                ) : (
                  <Folder size={15} color="#4285f4" />
                )}
                <span>Google Bucket</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setGoogleFolderExpanded(!googleFolderExpanded);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#9ca3af',
                  padding: '2px',
                  cursor: 'pointer',
                }}
              >
                {googleFolderExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              </button>
            </div>

            {/* Folder Sub-items (Gmail, Calendar, Drive) */}
            {googleFolderExpanded && (
              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  padding: '2px 8px 8px 24px',
                  gap: '2px',
                }}
              >
                <div
                  onClick={() => handleSelectGoogleTab('gmail')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '5px 10px',
                    borderRadius: '8px',
                    color: '#f87171',
                    fontSize: '12px',
                    cursor: 'pointer',
                    background: 'rgba(239, 68, 68, 0.06)',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(239, 68, 68, 0.06)')}
                >
                  <Mail size={12} />
                  <span>Gmail</span>
                </div>

                <div
                  onClick={() => handleSelectGoogleTab('calendar')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '5px 10px',
                    borderRadius: '8px',
                    color: '#60a5fa',
                    fontSize: '12px',
                    cursor: 'pointer',
                    background: 'rgba(59, 130, 246, 0.06)',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(59, 130, 246, 0.15)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(59, 130, 246, 0.06)')}
                >
                  <Calendar size={12} />
                  <span>Calendar</span>
                </div>

                <div
                  onClick={() => handleSelectGoogleTab('drive')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '5px 10px',
                    borderRadius: '8px',
                    color: '#34d399',
                    fontSize: '12px',
                    cursor: 'pointer',
                    background: 'rgba(52, 211, 153, 0.06)',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(52, 211, 153, 0.15)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(52, 211, 153, 0.06)')}
                >
                  <HardDrive size={12} />
                  <span>Drive</span>
                </div>

                <div
                  onClick={() => handleSelectGoogleTab('notes')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '5px 10px',
                    borderRadius: '8px',
                    color: '#fbbf24',
                    fontSize: '12px',
                    cursor: 'pointer',
                    background: 'rgba(245, 158, 11, 0.06)',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(245, 158, 11, 0.15)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(245, 158, 11, 0.06)')}
                >
                  <CheckSquare size={12} />
                  <span>Notes & Tasks</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* NON-CLICKABLE Agent & MCP Capabilities Showcase Guide */}
        <div style={{ padding: '4px 12px', display: 'flex', flexDirection: 'column' }}>
          <div
            onClick={() => setCapabilitiesExpanded(!capabilitiesExpanded)}
            style={{
              padding: '6px 6px',
              fontSize: '10px',
              fontWeight: 700,
              color: '#9ca3af',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
            }}
          >
            <span>Agent Capabilities Guide</span>
            {capabilitiesExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </div>

          {capabilitiesExpanded && (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '5px',
                maxHeight: '190px',
                overflowY: 'auto',
                paddingRight: '2px',
              }}
            >
              {mcpCapabilities.map((cap, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '7px 10px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.025)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '3px',
                    cursor: 'default', // Explicitly non-clickable as requested
                    userSelect: 'none',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {cap.icon}
                      <span style={{ fontSize: '11px', fontWeight: 600, color: '#f3f4f6' }}>
                        {cap.name}
                      </span>
                    </div>
                    <span
                      style={{
                        fontSize: '9px',
                        color: cap.color,
                        background: cap.bg,
                        padding: '1px 5px',
                        borderRadius: '4px',
                        fontWeight: 500,
                      }}
                    >
                      {cap.tag}
                    </span>
                  </div>
                  <p style={{ fontSize: '10px', color: '#9ca3af', lineHeight: 1.3, margin: 0 }}>
                    {cap.desc}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Chat History List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '8px 12px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
          <div style={{ padding: '6px 4px 4px 4px', fontSize: '10px', fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Recent Conversations
          </div>

          {chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => {
                setActiveView('chat');
                onSelectChat(chat.id);
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '7px 10px',
                borderRadius: '8px',
                background: chat.id === currentChatId && activeView === 'chat' ? 'rgba(168, 85, 247, 0.12)' : 'transparent',
                border: chat.id === currentChatId && activeView === 'chat' ? '1px solid rgba(168, 85, 247, 0.25)' : '1px solid transparent',
                color: chat.id === currentChatId && activeView === 'chat' ? '#f3f4f6' : '#9ca3af',
                fontSize: '12px',
                cursor: 'pointer',
                transition: 'background 0.15s',
              }}
              onMouseEnter={(e) => {
                if (chat.id !== currentChatId || activeView !== 'chat') e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
              }}
              onMouseLeave={(e) => {
                if (chat.id !== currentChatId || activeView !== 'chat') e.currentTarget.style.background = 'transparent';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                <MessageSquare size={13} style={{ flexShrink: 0, opacity: chat.id === currentChatId ? 1 : 0.6 }} />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{chat.title}</span>
              </div>
              {chats.length > 1 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#6b7280',
                    cursor: 'pointer',
                    padding: '2px',
                    opacity: 0.6,
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#ef4444')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = '#6b7280')}
                >
                  <Trash2 size={12} />
                </button>
              )}
            </div>
          ))}
        </div>
      </aside>
    </>
  );
}
