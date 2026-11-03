import React, { useState } from 'react';
import {
  Mail,
  Calendar,
  HardDrive,
  ShieldCheck,
  Sparkles,
  RefreshCw,
  PlusCircle,
  ExternalLink,
  Layers,
  ArrowRight,
  FileText,
  CheckCircle2,
  ChevronRight,
  CheckSquare
} from 'lucide-react';
import GmailView from './GmailView';
import CalendarView from './CalendarView';
import DriveView from './DriveView';
import NotesView from './NotesView';
import GoogleConnectModal from './GoogleConnectModal';

export default function GoogleHub({
  systemStatus,
  onRefreshStatus,
  onAskAgent,
  onNavigateChat,
  activeTab: controlledTab,
  setActiveTab: setControlledTab,
}) {
  const [internalTab, setInternalTab] = useState('gmail');
  const activeTab = controlledTab || internalTab;
  const setActiveTab = setControlledTab || setInternalTab;

  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [googlePrompt, setGooglePrompt] = useState('');

  const isConnected = systemStatus?.google?.authenticated;
  const userEmail = systemStatus?.google?.email || 'Not connected';

  const handleQuickAsk = (e) => {
    e.preventDefault();
    if (!googlePrompt.trim()) return;
    onAskAgent(googlePrompt);
    setGooglePrompt('');
    if (onNavigateChat) {
      onNavigateChat();
    }
  };

  const mcpModules = [
    {
      id: 'gmail',
      title: 'Gmail MCP',
      tag: 'Mail Server MCP',
      tagColor: '#ef4444',
      tagBg: 'rgba(239, 68, 68, 0.15)',
      desc: 'Retrieve unread emails, search inbox by query, draft replies, and send messages via Gmail API.',
      icon: <Mail size={20} color="#f87171" />,
      quickPrompt: 'Check my unread emails in Gmail',
    },
    {
      id: 'calendar',
      title: 'Calendar MCP',
      tag: 'Calendar Server MCP',
      tagColor: '#60a5fa',
      tagBg: 'rgba(59, 130, 246, 0.15)',
      desc: 'Inspect upcoming events, detect conflicts, schedule meetings, and create Google Meet links.',
      icon: <Calendar size={20} color="#60a5fa" />,
      quickPrompt: 'What do I have scheduled on my Google calendar for the next 7 days?',
    },
    {
      id: 'drive',
      title: 'Drive MCP',
      tag: 'Drive Server MCP',
      tagColor: '#34d399',
      tagBg: 'rgba(52, 211, 153, 0.15)',
      desc: 'Search Drive files, export Google Docs to plain text, inspect spreadsheets, and summarize content.',
      icon: <HardDrive size={20} color="#34d399" />,
      quickPrompt: 'What files are in my Google Drive?',
    },
    {
      id: 'notes',
      title: 'Notes & Tasks MCP',
      tag: 'Notes & Keep MCP',
      tagColor: '#f59e0b',
      tagBg: 'rgba(245, 158, 11, 0.15)',
      desc: 'Sync notes and to-dos with Google Keep/Tasks, add reminders, check off completed items, and search.',
      icon: <CheckSquare size={20} color="#fbbf24" />,
      quickPrompt: 'List all my notes and pending tasks from Google',
    },
  ];

  return (
    <div
      className="google-hub-container"
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflowY: 'auto',
        maxWidth: '1280px',
        margin: '0 auto',
        width: '100%',
      }}
    >
      {/* Top Banner / Hero Card */}
      <div
        style={{
          borderRadius: '24px',
          background: 'linear-gradient(135deg, rgba(30, 31, 38, 0.9) 0%, rgba(20, 21, 26, 0.9) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '22px 26px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '20px',
          flexWrap: 'wrap',
          boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.5)',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div
            style={{
              width: '50px',
              height: '50px',
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #4285F4 0%, #EA4335 33%, #FBBC05 66%, #34A853 100%)',
              padding: '2px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 24px rgba(66, 133, 244, 0.25)',
            }}
          >
            <div
              style={{
                width: '100%',
                height: '100%',
                borderRadius: '14px',
                background: '#16161b',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <ShieldCheck size={24} color="#60a5fa" />
            </div>
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f3f4f6', letterSpacing: '-0.02em' }}>
                Google Workspace Bucket
              </h1>
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px',
                  padding: '3px 10px',
                  borderRadius: '20px',
                  fontSize: '11px',
                  fontWeight: 600,
                  background: isConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                  color: isConnected ? '#34d399' : '#f87171',
                  border: isConnected ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)',
                }}
              >
                <span
                  style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: isConnected ? '#10b981' : '#ef4444',
                  }}
                />
                {isConnected ? 'MCP Services Live' : 'Disconnected'}
              </span>
            </div>
            <p style={{ fontSize: '13px', color: '#9ca3af', marginTop: '3px' }}>
              {isConnected
                ? `Authorized for account: ${userEmail}`
                : 'Connect your real Google account to grant your agent access to Gmail, Calendar, and Drive.'}
            </p>
          </div>
        </div>

        {/* Connect / Manage Account Button */}
        <button
          onClick={() => setIsConnectModalOpen(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            borderRadius: '14px',
            background: isConnected
              ? 'rgba(255, 255, 255, 0.08)'
              : 'linear-gradient(135deg, #4285F4 0%, #34A853 100%)',
            border: isConnected ? '1px solid rgba(255, 255, 255, 0.12)' : 'none',
            color: '#fff',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: isConnected ? 'none' : '0 4px 16px rgba(66, 133, 244, 0.3)',
            transition: 'transform 0.15s, opacity 0.15s',
          }}
        >
          <ShieldCheck size={16} />
          <span>{isConnected ? 'Manage Google Account' : 'Connect Real Google Account'}</span>
        </button>
      </div>

      {/* Google MCP Modules Showcase Cards */}
      <div style={{ marginBottom: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <h2 style={{ fontSize: '12px', fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Connected Google MCP Protocols
          </h2>
          <span style={{ fontSize: '11px', color: '#6b7280' }}>
            All 4 modules powered by Model Context Protocol (MCP)
          </span>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '12px',
          }}
        >
          {mcpModules.map((m) => {
            const isTabMatch = activeTab === m.id;
            return (
              <div
                key={m.id}
                onClick={() => {
                  setActiveTab(m.id);
                }}
                style={{
                  padding: '14px 16px',
                  borderRadius: '16px',
                  background: isTabMatch ? 'rgba(255, 255, 255, 0.06)' : 'rgba(255, 255, 255, 0.025)',
                  border: isTabMatch ? `1px solid ${m.tagColor}80` : '1px solid rgba(255, 255, 255, 0.06)',
                  cursor: 'pointer',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '8px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)';
                  e.currentTarget.style.borderColor = `${m.tagColor}60`;
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = isTabMatch ? 'rgba(255, 255, 255, 0.06)' : 'rgba(255, 255, 255, 0.025)';
                  e.currentTarget.style.borderColor = isTabMatch ? `${m.tagColor}80` : '1px solid rgba(255, 255, 255, 0.06)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <div
                      style={{
                        padding: '6px',
                        borderRadius: '8px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {m.icon}
                    </div>
                    <span
                      style={{
                        fontSize: '10px',
                        fontWeight: 600,
                        color: m.tagColor,
                        background: m.tagBg,
                        padding: '2px 8px',
                        borderRadius: '6px',
                      }}
                    >
                      {m.tag}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#f3f4f6', marginBottom: '4px' }}>
                    {m.title}
                  </h3>
                  <p style={{ fontSize: '11px', color: '#9ca3af', lineHeight: 1.4 }}>
                    {m.desc}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '6px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <span style={{ fontSize: '11px', color: m.tagColor, fontWeight: 500, display: 'flex', alignItems: 'center', gap: '3px' }}>
                    {m.id === 'docs_tasks' ? 'Ask Agent' : 'View Module'} <ChevronRight size={12} />
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onAskAgent(m.quickPrompt);
                    }}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#a855f7',
                      fontSize: '10px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '3px',
                      padding: '2px 6px',
                      borderRadius: '4px',
                    }}
                  >
                    <Sparkles size={10} /> Quick Query
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Tabs Navigation */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          paddingBottom: '10px',
          marginBottom: '18px',
        }}
      >
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setActiveTab('gmail')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              borderRadius: '12px',
              background: activeTab === 'gmail' ? 'rgba(239, 68, 68, 0.15)' : 'transparent',
              border: activeTab === 'gmail' ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid transparent',
              color: activeTab === 'gmail' ? '#f87171' : '#9ca3af',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            <Mail size={15} />
            <span>Gmail MCP View</span>
          </button>

          <button
            onClick={() => setActiveTab('calendar')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              borderRadius: '12px',
              background: activeTab === 'calendar' ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
              border: activeTab === 'calendar' ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid transparent',
              color: activeTab === 'calendar' ? '#60a5fa' : '#9ca3af',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            <Calendar size={15} />
            <span>Calendar MCP View</span>
          </button>

          <button
            onClick={() => setActiveTab('drive')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              borderRadius: '12px',
              background: activeTab === 'drive' ? 'rgba(52, 211, 153, 0.15)' : 'transparent',
              border: activeTab === 'drive' ? '1px solid rgba(52, 211, 153, 0.3)' : '1px solid transparent',
              color: activeTab === 'drive' ? '#34d399' : '#9ca3af',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            <HardDrive size={15} />
            <span>Drive MCP View</span>
          </button>

          <button
            onClick={() => setActiveTab('notes')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              borderRadius: '12px',
              background: activeTab === 'notes' ? 'rgba(245, 158, 11, 0.15)' : 'transparent',
              border: activeTab === 'notes' ? '1px solid rgba(245, 158, 11, 0.3)' : '1px solid transparent',
              color: activeTab === 'notes' ? '#fbbf24' : '#9ca3af',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            <CheckSquare size={15} />
            <span>Notes & Tasks MCP View</span>
          </button>
        </div>

        <span style={{ fontSize: '11px', color: '#6b7280' }}>
          Live Workspace Sync Active
        </span>
      </div>

      {/* Feature Views */}
      <div style={{ flex: 1, marginBottom: '20px' }}>
        {activeTab === 'gmail' && <GmailView onAskAgent={onAskAgent} />}
        {activeTab === 'calendar' && <CalendarView onAskAgent={onAskAgent} />}
        {activeTab === 'drive' && <DriveView onAskAgent={onAskAgent} />}
        {activeTab === 'notes' && <NotesView onAskAgent={onAskAgent} />}
      </div>

      {/* Scoped Google Assistant Input */}
      <div
        style={{
          marginTop: 'auto',
          padding: '16px 20px',
          borderRadius: '18px',
          background: 'rgba(20, 21, 26, 0.85)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <Sparkles size={14} color="#c084fc" />
          <span style={{ fontSize: '12px', fontWeight: 600, color: '#c084fc' }}>
            Ask Google Workspace MCP Agent
          </span>
          <span style={{ fontSize: '11px', color: '#6b7280' }}>
            (Queries execute via MCP tools on your authenticated account)
          </span>
        </div>

        <form onSubmit={handleQuickAsk} style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={googlePrompt}
            onChange={(e) => setGooglePrompt(e.target.value)}
            placeholder={
              activeTab === 'gmail'
                ? 'Ask about your emails (e.g., "Check unread emails from John and draft a reply")'
                : activeTab === 'calendar'
                ? 'Ask about your agenda (e.g., "What meetings do I have tomorrow? Schedule sync at 4pm")'
                : activeTab === 'notes'
                ? 'Ask about your notes or tasks (e.g., "Add note: finish presentation deck", "What tasks are pending?")'
                : 'Ask about Drive (e.g., "Find the latest quarterly report and summarize it")'
            }
            style={{
              flex: 1,
              padding: '10px 14px',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              color: '#f3f4f6',
              fontSize: '13px',
              outline: 'none',
            }}
          />
          <button
            type="submit"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '10px 18px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)',
              border: 'none',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <span>Ask Agent</span>
            <ArrowRight size={14} />
          </button>
        </form>
      </div>

      {/* Google Connect Modal */}
      <GoogleConnectModal
        isOpen={isConnectModalOpen}
        onClose={() => setIsConnectModalOpen(false)}
        systemStatus={systemStatus}
        onRefreshStatus={onRefreshStatus}
      />
    </div>
  );
}
