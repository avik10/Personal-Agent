import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  RefreshCw,
  X,
  Mail,
  Calendar,
  HardDrive,
  LogOut,
  Key,
  ExternalLink
} from 'lucide-react';
import { getApiUrl } from '../../config/api';

export default function GoogleConnectModal({
  isOpen,
  onClose,
  systemStatus,
  onRefreshStatus
}) {
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [authError, setAuthError] = useState(null);
  const [authSuccess, setAuthSuccess] = useState(null);

  const isConnected = systemStatus?.google?.authenticated;
  const email = systemStatus?.google?.email;

  // Check URL parameters for OAuth redirect feedback
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('google_auth') === 'success') {
        setAuthSuccess('Google Workspace connected successfully!');
        if (onRefreshStatus) onRefreshStatus();
        window.history.replaceState({}, document.title, window.location.pathname);
      } else if (urlParams.get('google_auth') === 'error') {
        setAuthError(`Google authorization failed: ${urlParams.get('detail') || 'access denied'}`);
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }
  }, []);

  if (!isOpen) return null;

  const handleRedirectToGoogleAuth = () => {
    setIsAuthenticating(true);
    // Direct browser redirect for Google OAuth 2.0 permission
    window.location.href = getApiUrl('/api/google/auth/login');
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Are you sure you want to disconnect your Google account?')) return;
    try {
      await fetch(getApiUrl('/api/google/auth/disconnect'), { method: 'POST' });
      if (onRefreshStatus) onRefreshStatus();
      setAuthSuccess('Google account disconnected.');
    } catch (err) {
      setAuthError('Failed to disconnect Google account.');
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
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
          maxWidth: '520px',
          background: '#16161b',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '24px',
          padding: '26px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(66, 133, 244, 0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #4285f4 0%, #34a853 50%, #fbbc05 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <ShieldCheck size={20} color="#fff" />
            </div>
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#f3f4f6' }}>
                Google Workspace Connection
              </h2>
              <p style={{ fontSize: '12px', color: '#9ca3af' }}>
                One-click OAuth 2.0 permission redirect
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#9ca3af',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: '8px',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Current Status Card */}
        <div
          style={{
            padding: '16px',
            borderRadius: '16px',
            background: isConnected ? 'rgba(16, 185, 129, 0.08)' : 'rgba(245, 158, 11, 0.08)',
            border: isConnected
              ? '1px solid rgba(16, 185, 129, 0.25)'
              : '1px solid rgba(245, 158, 11, 0.25)',
            marginBottom: '18px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {isConnected ? (
                <CheckCircle2 size={18} color="#10b981" />
              ) : (
                <AlertCircle size={18} color="#f59e0b" />
              )}
              <span
                style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  color: isConnected ? '#10b981' : '#f59e0b',
                }}
              >
                {isConnected ? 'Connected & Authorized' : 'Not Connected'}
              </span>
            </div>
            <button
              onClick={onRefreshStatus}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                padding: '4px 8px',
                borderRadius: '8px',
                color: '#d1d5db',
                fontSize: '11px',
                cursor: 'pointer',
              }}
            >
              <RefreshCw size={11} /> Refresh
            </button>
          </div>

          {isConnected ? (
            <div style={{ marginTop: '10px' }}>
              <p style={{ fontSize: '13px', color: '#e5e7eb' }}>
                Account: <strong>{email}</strong>
              </p>
              <p style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>
                Agent has real-time access to Gmail, Calendar, and Drive through Model Context Protocol (MCP).
              </p>
            </div>
          ) : (
            <div style={{ marginTop: '10px' }}>
              <p style={{ fontSize: '13px', color: '#e5e7eb' }}>
                Click the button below to be redirected to Google's consent screen.
              </p>
            </div>
          )}
        </div>

        {/* Feedback Alerts */}
        {authSuccess && (
          <div style={{ padding: '10px 14px', borderRadius: '12px', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', fontSize: '12px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={16} />
            <span>{authSuccess}</span>
          </div>
        )}

        {authError && (
          <div style={{ padding: '10px 14px', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.15)', color: '#f87171', fontSize: '12px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} />
            <span>{authError}</span>
          </div>
        )}

        {/* Redirect for Google Auth Permission Button */}
        <div style={{ marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <button
            onClick={handleRedirectToGoogleAuth}
            disabled={isAuthenticating}
            style={{
              width: '100%',
              padding: '12px 18px',
              borderRadius: '12px',
              background: '#ffffff',
              color: '#1f2937',
              fontSize: '14px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px',
              border: 'none',
              cursor: isAuthenticating ? 'not-allowed' : 'pointer',
              boxShadow: '0 4px 14px rgba(0, 0, 0, 0.3)',
              transition: 'transform 0.15s, opacity 0.15s',
              opacity: isAuthenticating ? 0.8 : 1,
            }}
          >
            {/* Google SVG Logo */}
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.15z"
              />
              <path
                fill="#34A853"
                d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.24v3.15C3.26 21.36 7.34 24 12 24z"
              />
              <path
                fill="#FBBC05"
                d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.24C.45 8.15 0 9.92 0 12s.45 3.85 1.24 5.42l4.04-3.15z"
              />
              <path
                fill="#EA4335"
                d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.24 6.58l4.04 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
              />
            </svg>
            <span>
              {isAuthenticating
                ? 'Redirecting to Google...'
                : isConnected
                ? 'Re-authenticate with Google'
                : 'Sign in with Google'}
            </span>
          </button>

          {isConnected && (
            <button
              onClick={handleDisconnect}
              style={{
                width: '100%',
                padding: '9px 14px',
                borderRadius: '10px',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                color: '#f87171',
                fontSize: '12px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                cursor: 'pointer',
              }}
            >
              <LogOut size={14} />
              <span>Disconnect Google Account</span>
            </button>
          )}
        </div>

        {/* Services Enabled Grid */}
        <div>
          <h3 style={{ fontSize: '11px', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', marginBottom: '8px' }}>
            Authorized Services Scope
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <div style={{ padding: '8px 10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Mail size={14} color="#f87171" />
              <div>
                <p style={{ fontSize: '11px', fontWeight: 600, color: '#f3f4f6' }}>Gmail</p>
                <p style={{ fontSize: '10px', color: '#9ca3af' }}>Read & send</p>
              </div>
            </div>
            <div style={{ padding: '8px 10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Calendar size={14} color="#60a5fa" />
              <div>
                <p style={{ fontSize: '11px', fontWeight: 600, color: '#f3f4f6' }}>Calendar</p>
                <p style={{ fontSize: '10px', color: '#9ca3af' }}>Agendas & Meet</p>
              </div>
            </div>
            <div style={{ padding: '8px 10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HardDrive size={14} color="#34d399" />
              <div>
                <p style={{ fontSize: '11px', fontWeight: 600, color: '#f3f4f6' }}>Drive</p>
                <p style={{ fontSize: '10px', color: '#9ca3af' }}>Docs & Sheets</p>
              </div>
            </div>
            <div style={{ padding: '8px 10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Key size={14} color="#c084fc" />
              <div>
                <p style={{ fontSize: '11px', fontWeight: 600, color: '#f3f4f6' }}>Docs & Tasks</p>
                <p style={{ fontSize: '10px', color: '#9ca3af' }}>Task lists</p>
              </div>
            </div>
          </div>
        </div>

        {/* Close Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 18px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #a855f7 0%, #3b82f6 100%)',
              border: 'none',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
