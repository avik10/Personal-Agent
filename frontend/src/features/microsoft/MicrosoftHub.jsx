import React, { useState } from 'react';
import {
  Mail,
  ShieldCheck,
  Sparkles,
  RefreshCw,
  ExternalLink,
  Layers,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
} from 'lucide-react';
import OutlookView from './OutlookView';
import OutlookConnectModal from './OutlookConnectModal';

export default function MicrosoftHub({
  systemStatus,
  onRefreshStatus,
  onAskAgent,
  onNavigateChat,
  activeTab: controlledTab,
  setActiveTab: setControlledTab,
}) {
  const [internalTab, setInternalTab] = useState('outlook');
  const activeTab = controlledTab || internalTab;
  const setActiveTab = setControlledTab || setInternalTab;

  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [promptInput, setPromptInput] = useState('');

  const isConnected = systemStatus?.microsoft?.authenticated;
  const userEmail = systemStatus?.microsoft?.email || 'Not connected';

  const handleQuickAsk = (e) => {
    e.preventDefault();
    if (!promptInput.trim()) return;
    onAskAgent(promptInput);
    setPromptInput('');
    if (onNavigateChat) {
      onNavigateChat();
    }
  };

  const mcpModules = [
    {
      id: 'outlook',
      title: 'Outlook MCP',
      tag: 'Mail Server MCP',
      tagColor: '#0078d4',
      tagBg: 'rgba(0, 120, 212, 0.15)',
      desc: 'Retrieve unread Outlook emails, search mailbox by query, draft replies, and send messages via Microsoft Graph API.',
      icon: <Mail size={20} color="#0078d4" />,
    },
  ];

  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 60px)',
        overflowY: 'auto',
        background: 'var(--bg-primary)',
      }}
    >
      <div style={{ maxWidth: '1100px', width: '100%', margin: '0 auto', padding: '24px 20px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Top Hero Banner */}
        <div
          style={{
            padding: '24px 28px',
            borderRadius: '24px',
            background: 'linear-gradient(135deg, rgba(0, 120, 212, 0.12) 0%, rgba(2, 132, 199, 0.05) 50%, rgba(14, 14, 17, 0.8) 100%)',
            border: '1px solid rgba(0, 120, 212, 0.25)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div
                style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '16px',
                  background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 8px 24px rgba(0, 120, 212, 0.4)',
                }}
              >
                <Mail size={28} color="#fff" />
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <h1 style={{ fontSize: '22px', fontWeight: 700, color: '#f3f4f6', margin: 0, letterSpacing: '-0.02em' }}>
                    Microsoft Bucket
                  </h1>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: isConnected ? '#34d399' : '#f87171',
                      background: isConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                      padding: '3px 10px',
                      borderRadius: '20px',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                    }}
                  >
                    {isConnected ? <CheckCircle2 size={12} /> : <ShieldCheck size={12} />}
                    {isConnected ? 'Connected' : 'Offline'}
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: '#9ca3af', margin: '4px 0 0 0' }}>
                  Live integration for Microsoft Outlook & Office 365 powered by Model Context Protocol (MCP).
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <button
                onClick={() => setIsConnectModalOpen(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 18px',
                  borderRadius: '12px',
                  background: isConnected ? 'rgba(255, 255, 255, 0.06)' : 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                  border: isConnected ? '1px solid rgba(255, 255, 255, 0.12)' : 'none',
                  color: '#fff',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  boxShadow: isConnected ? 'none' : '0 4px 14px rgba(0, 120, 212, 0.35)',
                }}
              >
                <ShieldCheck size={16} />
                <span>{isConnected ? 'Manage Microsoft Account' : 'Connect Account'}</span>
              </button>
            </div>
          </div>

          {/* Quick AI Ask bar for Outlook */}
          <form
            onSubmit={handleQuickAsk}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid rgba(0, 120, 212, 0.3)',
              borderRadius: '14px',
              padding: '6px 8px 6px 14px',
            }}
          >
            <Sparkles size={16} color="#0078d4" />
            <input
              type="text"
              value={promptInput}
              onChange={(e) => setPromptInput(e.target.value)}
              placeholder="Ask AI: 'Summarize my unread Outlook emails' or 'Send an Outlook email to...'"
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                color: '#f3f4f6',
                fontSize: '13px',
                outline: 'none',
              }}
            />
            <button
              type="submit"
              disabled={!promptInput.trim()}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                borderRadius: '10px',
                background: promptInput.trim() ? '#0078d4' : 'rgba(255, 255, 255, 0.05)',
                border: 'none',
                color: promptInput.trim() ? '#fff' : '#6b7280',
                fontSize: '12px',
                fontWeight: 600,
                cursor: promptInput.trim() ? 'pointer' : 'default',
              }}
            >
              <span>Ask Agent</span>
              <ArrowRight size={13} />
            </button>
          </form>
        </div>

        {/* Modules Tab Selection */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid rgba(255, 255, 255, 0.06)', paddingBottom: '12px' }}>
          {mcpModules.map((mod) => {
            const isTabActive = activeTab === mod.id;
            return (
              <button
                key={mod.id}
                onClick={() => setActiveTab(mod.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '9px 18px',
                  borderRadius: '12px',
                  background: isTabActive ? 'rgba(0, 120, 212, 0.18)' : 'rgba(255, 255, 255, 0.03)',
                  border: isTabActive ? '1px solid rgba(0, 120, 212, 0.45)' : '1px solid rgba(255, 255, 255, 0.06)',
                  color: isTabActive ? '#60a5fa' : '#9ca3af',
                  fontSize: '13px',
                  fontWeight: isTabActive ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                {mod.icon}
                <span>{mod.title}</span>
              </button>
            );
          })}
        </div>

        {/* Active Module View */}
        <div>
          {activeTab === 'outlook' && (
            <OutlookView
              onAskAgent={onAskAgent}
              onOpenConnectModal={() => setIsConnectModalOpen(true)}
              isConnected={isConnected}
              userEmail={userEmail}
            />
          )}
        </div>
      </div>

      {/* Connect Modal */}
      <OutlookConnectModal
        isOpen={isConnectModalOpen}
        onClose={() => setIsConnectModalOpen(false)}
        systemStatus={systemStatus}
        onRefreshStatus={onRefreshStatus}
      />
    </div>
  );
}
