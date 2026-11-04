import React, { useState } from 'react';
import {
  X,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  Mail,
  Key,
  Globe,
  RefreshCw,
  LogOut
} from 'lucide-react';
import { getApiUrl } from '../../config/api';

export default function OutlookConnectModal({
  isOpen,
  onClose,
  systemStatus,
  onRefreshStatus,
}) {
  const [copiedField, setCopiedField] = useState(null);
  const [isDisconnecting, setIsDisconnecting] = useState(false);

  if (!isOpen) return null;

  const isConnected = systemStatus?.microsoft?.authenticated;
  const userEmail = systemStatus?.microsoft?.email || 'Not connected';

  const currentOrigin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000';
  const backendBase = getApiUrl('').replace(/\/api$/, '');
  const callbackUrl = `${backendBase}/api/outlook/auth/callback`;

  const copyToClipboard = (text, fieldName) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Are you sure you want to disconnect your Microsoft Outlook account?')) return;
    setIsDisconnecting(true);
    try {
      await fetch(getApiUrl('/api/outlook/auth/disconnect'), { method: 'POST' });
      if (onRefreshStatus) await onRefreshStatus();
    } catch (e) {
      console.error('Failed to disconnect Outlook:', e);
    } finally {
      setIsDisconnecting(false);
    }
  };

  const handleStartAuth = () => {
    window.location.href = getApiUrl('/api/outlook/auth/login');
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '560px',
          background: '#16161b',
          border: '1px solid rgba(0, 120, 212, 0.3)',
          borderRadius: '20px',
          padding: '24px',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 120, 212, 0.15)',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(0, 120, 212, 0.4)',
              }}
            >
              <Mail size={22} color="#fff" />
            </div>
            <div>
              <h2 style={{ fontSize: '17px', fontWeight: 700, color: '#f3f4f6', margin: 0 }}>
                Microsoft Outlook Integration
              </h2>
              <p style={{ fontSize: '12px', color: '#9ca3af', margin: '2px 0 0 0' }}>
                Microsoft Graph API & Outlook MCP Server
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#9ca3af',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: '8px',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Live Status Banner */}
        <div
          style={{
            padding: '14px 16px',
            borderRadius: '12px',
            background: isConnected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(0, 120, 212, 0.08)',
            border: isConnected ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(0, 120, 212, 0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {isConnected ? (
              <CheckCircle2 size={20} color="#10b981" />
            ) : (
              <ShieldCheck size={20} color="#0078d4" />
            )}
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#f3f4f6' }}>
                {isConnected ? 'Outlook Account Connected' : 'Outlook Account Not Connected'}
              </div>
              <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>
                {isConnected ? userEmail : 'Sign in to access your Outlook inbox, search, and send emails.'}
              </div>
            </div>
          </div>

          {isConnected ? (
            <button
              onClick={handleDisconnect}
              disabled={isDisconnecting}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                borderRadius: '8px',
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#f87171',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <LogOut size={12} />
              <span>{isDisconnecting ? 'Disconnecting...' : 'Disconnect'}</span>
            </button>
          ) : (
            <button
              onClick={handleStartAuth}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '9px 16px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                border: 'none',
                color: '#fff',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(0, 120, 212, 0.35)',
              }}
            >
              <Mail size={15} />
              <span>Sign in with Microsoft</span>
            </button>
          )}
        </div>

        {/* Features Overview */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Supported Outlook MCP Capabilities
          </span>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
            {[
              { label: 'Inbox & Unread Fetch', desc: 'Live email listing with unread tags' },
              { label: 'Keyword Search', desc: 'Search by sender, subject, or content' },
              { label: 'Compose & Send Mail', desc: 'Send emails via Outlook Graph API' },
              { label: 'AI Summaries & Drafts', desc: 'Multi-agent reading & drafting' },
            ].map((f, i) => (
              <div
                key={i}
                style={{
                  padding: '10px 12px',
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                }}
              >
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#f3f4f6' }}>{f.label}</div>
                <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>{f.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Azure App Setup Guide (Collapsible or clear instructions) */}
        <div
          style={{
            padding: '14px',
            borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.07)',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#0078d4', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Key size={13} />
              Azure App Registration Details
            </span>
            <a
              href="https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade"
              target="_blank"
              rel="noreferrer"
              style={{
                fontSize: '11px',
                color: '#60a5fa',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                textDecoration: 'none',
              }}
            >
              <span>Azure Portal</span>
              <ExternalLink size={11} />
            </a>
          </div>

          <p style={{ fontSize: '11px', color: '#9ca3af', margin: 0, lineHeight: 1.5 }}>
            To authenticate with personal or work Microsoft accounts, register a free app in Azure Portal with
            supported account type <em>"Personal Microsoft accounts and organizational directories"</em>.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ fontSize: '11px', color: '#d1d5db', fontWeight: 500 }}>
              OAuth 2.0 Web Redirect URI:
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '8px 10px',
                borderRadius: '8px',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                fontSize: '11px',
                fontFamily: 'monospace',
                color: '#93c5fd',
              }}
            >
              <span style={{ wordBreak: 'break-all' }}>{callbackUrl}</span>
              <button
                onClick={() => copyToClipboard(callbackUrl, 'redirect_uri')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#9ca3af',
                  cursor: 'pointer',
                  padding: '2px 4px',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                {copiedField === 'redirect_uri' ? <Check size={13} color="#10b981" /> : <Copy size={13} />}
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 16px',
              borderRadius: '10px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#d1d5db',
              fontSize: '12px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            Close
          </button>
          {!isConnected && (
            <button
              onClick={handleStartAuth}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 18px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                border: 'none',
                color: '#fff',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <Mail size={14} />
              <span>Connect Outlook</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
