import React, { useState, useEffect } from 'react';
import {
  Mail,
  Search,
  RefreshCw,
  Send,
  Sparkles,
  Inbox,
  Clock,
  User,
  CheckCircle2,
  AlertCircle,
  Reply,
  X,
  FileText,
  Paperclip,
  CheckSquare
} from 'lucide-react';
import { getApiUrl } from '../../config/api';

export default function OutlookView({ onAskAgent, onOpenConnectModal, isConnected, userEmail }) {
  const [emails, setEmails] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFolder, setActiveFolder] = useState('inbox');
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);

  // Compose State
  const [showCompose, setShowCompose] = useState(false);
  const [sendForm, setSendForm] = useState({ to: '', subject: '', body: '' });
  const [isSending, setIsSending] = useState(false);
  const [sendStatus, setSendStatus] = useState(null);

  const fetchEmails = async () => {
    if (!isConnected) return;
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('folder', activeFolder);
      params.append('max_results', '20');
      if (unreadOnly) params.append('unread_only', 'true');
      if (searchQuery.trim()) params.append('query', searchQuery.trim());

      const res = await fetch(getApiUrl(`/api/outlook/messages?${params.toString()}`));
      if (res.ok) {
        const data = await res.json();
        setEmails(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch Outlook emails:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, [isConnected, activeFolder, unreadOnly]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchEmails();
  };

  const handleReplyDirectly = (msg) => {
    const targetEmail = msg.from_email || msg.from || '';
    const cleanSubject = msg.subject || '';
    const replySubject = cleanSubject.toLowerCase().startsWith('re:') ? cleanSubject : `Re: ${cleanSubject}`;

    setSendForm({
      to: targetEmail,
      subject: replySubject,
      body: `\n\n--- On ${msg.receivedDateTime ? new Date(msg.receivedDateTime).toLocaleString() : 'recent'}, ${msg.from} wrote:\n> ${msg.bodyPreview || ''}`,
    });
    setSendStatus(null);
    setShowCompose(true);
  };

  const handleSendEmail = async (e) => {
    e.preventDefault();
    if (!sendForm.to.trim() || !sendForm.subject.trim()) return;

    setIsSending(true);
    setSendStatus(null);

    try {
      const res = await fetch(getApiUrl('/api/outlook/messages/send'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: sendForm.to.trim(),
          subject: sendForm.subject.trim(),
          body: sendForm.body.trim(),
          is_html: false,
        }),
      });

      if (res.ok) {
        setSendStatus({ success: true, message: `Email sent via Outlook to ${sendForm.to}` });
        setSendForm({ to: '', subject: '', body: '' });
        setTimeout(() => {
          setShowCompose(false);
          setSendStatus(null);
          fetchEmails();
        }, 1500);
      } else {
        const err = await res.json();
        setSendStatus({ success: false, message: err.detail || 'Failed to send email' });
      }
    } catch (err) {
      setSendStatus({ success: false, message: err.message || 'Network error sending email' });
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
      {/* Top Banner & Sync Notice */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 18px',
          borderRadius: '14px',
          background: isConnected ? 'rgba(0, 120, 212, 0.08)' : 'rgba(239, 68, 68, 0.08)',
          border: isConnected ? '1px solid rgba(0, 120, 212, 0.25)' : '1px solid rgba(239, 68, 68, 0.25)',
          gap: '12px',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Mail size={18} color={isConnected ? '#0078d4' : '#f87171'} />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#f3f4f6' }}>
              {isConnected ? `Connected: ${userEmail}` : 'Microsoft Outlook Disconnected'}
            </div>
            <div style={{ fontSize: '11px', color: '#9ca3af' }}>
              {isConnected
                ? 'Emails sync directly through Microsoft Graph MCP. Separate from Google Workspace.'
                : 'Connect your Microsoft/Outlook account to read, search, and send emails.'}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {!isConnected && (
            <button
              onClick={onOpenConnectModal}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                border: 'none',
                color: '#fff',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <span>Connect Outlook</span>
            </button>
          )}

          {isConnected && (
            <button
              onClick={() => {
                setShowCompose(true);
                setSendStatus(null);
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                border: 'none',
                color: '#fff',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(0, 120, 212, 0.3)',
              }}
            >
              <Send size={13} />
              <span>Compose Email</span>
            </button>
          )}
        </div>
      </div>

      {/* Search & Folder Controls */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          flexWrap: 'wrap',
        }}
      >
        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search
            size={16}
            color="#9ca3af"
            style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }}
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Outlook emails by keyword, sender, or subject..."
            style={{
              width: '100%',
              padding: '10px 14px 10px 38px',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              color: '#f3f4f6',
              fontSize: '13px',
              outline: 'none',
            }}
          />
        </form>

        {/* Folder Selectors */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {[
            { id: 'inbox', label: 'Inbox' },
            { id: 'sentitems', label: 'Sent' },
            { id: 'drafts', label: 'Drafts' },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => {
                setActiveFolder(f.id);
                setSearchQuery('');
              }}
              style={{
                padding: '7px 12px',
                borderRadius: '10px',
                background: activeFolder === f.id ? 'rgba(0, 120, 212, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                border: activeFolder === f.id ? '1px solid rgba(0, 120, 212, 0.5)' : '1px solid rgba(255, 255, 255, 0.06)',
                color: activeFolder === f.id ? '#60a5fa' : '#9ca3af',
                fontSize: '12px',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              {f.label}
            </button>
          ))}

          {/* Unread Filter Toggle */}
          <button
            onClick={() => setUnreadOnly(!unreadOnly)}
            style={{
              padding: '7px 12px',
              borderRadius: '10px',
              background: unreadOnly ? 'rgba(0, 120, 212, 0.25)' : 'rgba(255, 255, 255, 0.04)',
              border: unreadOnly ? '1px solid #0078d4' : '1px solid rgba(255, 255, 255, 0.06)',
              color: unreadOnly ? '#93c5fd' : '#9ca3af',
              fontSize: '12px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            Unread
          </button>

          <button
            onClick={fetchEmails}
            disabled={isLoading || !isConnected}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              borderRadius: '10px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#d1d5db',
              fontSize: '12px',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Email List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {!isConnected ? (
          <div
            style={{
              padding: '60px 20px',
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '16px',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '14px',
                background: 'rgba(0, 120, 212, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Mail size={24} color="#0078d4" />
            </div>
            <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#f3f4f6', margin: 0 }}>
              Connect Your Microsoft Outlook Account
            </h3>
            <p style={{ fontSize: '12px', color: '#9ca3af', maxWidth: '420px', margin: 0, lineHeight: 1.5 }}>
              Link your `@outlook.com`, `@hotmail.com`, or Office 365 account to search messages,
              read emails, and send messages via the Microsoft Graph MCP Server.
            </p>
            <button
              onClick={onOpenConnectModal}
              style={{
                marginTop: '6px',
                padding: '9px 20px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                border: 'none',
                color: '#fff',
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Sign in with Microsoft
            </button>
          </div>
        ) : isLoading && emails.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af', fontSize: '13px' }}>
            Loading Outlook emails via Microsoft Graph...
          </div>
        ) : emails.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280', fontSize: '13px' }}>
            No emails found in Outlook {activeFolder}.
          </div>
        ) : (
          emails.map((msg) => {
            const isUnread = !msg.isRead;
            return (
              <div
                key={msg.id}
                onClick={() => setSelectedEmail(msg)}
                style={{
                  padding: '14px 16px',
                  borderRadius: '12px',
                  background: isUnread ? 'rgba(0, 120, 212, 0.06)' : 'rgba(255, 255, 255, 0.02)',
                  border: isUnread ? '1px solid rgba(0, 120, 212, 0.3)' : '1px solid rgba(255, 255, 255, 0.05)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: '12px',
                  cursor: 'pointer',
                  transition: 'background 0.15s, border-color 0.15s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = isUnread ? 'rgba(0, 120, 212, 0.1)' : 'rgba(255, 255, 255, 0.04)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = isUnread ? 'rgba(0, 120, 212, 0.06)' : 'rgba(255, 255, 255, 0.02)';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', flex: 1, minWidth: 0 }}>
                  {/* Unread indicator */}
                  <div style={{ marginTop: '5px', width: '8px', height: '8px', borderRadius: '50%', background: isUnread ? '#0078d4' : 'transparent', flexShrink: 0 }} />

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                      <span style={{ fontSize: '13px', fontWeight: isUnread ? 700 : 500, color: isUnread ? '#f3f4f6' : '#d1d5db', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {msg.from}
                      </span>
                      {msg.receivedDateTime && (
                        <span style={{ fontSize: '11px', color: '#6b7280', flexShrink: 0 }}>
                          {new Date(msg.receivedDateTime).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>

                    <div style={{ fontSize: '13px', fontWeight: isUnread ? 600 : 500, color: '#f3f4f6', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {msg.subject}
                    </div>

                    <p style={{ fontSize: '12px', color: '#9ca3af', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', lineHeight: 1.4 }}>
                      {msg.bodyPreview || 'No preview text.'}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }} onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => handleReplyDirectly(msg)}
                    title="Reply to this email"
                    style={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      color: '#d1d5db',
                      borderRadius: '8px',
                      padding: '5px 8px',
                      fontSize: '11px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <Reply size={12} />
                    <span>Reply</span>
                  </button>

                  <button
                    onClick={() => onAskAgent(`Regarding my Outlook email from "${msg.from}" with subject "${msg.subject}": summarize key points and propose action steps`)}
                    title="Ask AI Agent to summarize and analyze"
                    style={{
                      background: 'rgba(0, 120, 212, 0.15)',
                      border: '1px solid rgba(0, 120, 212, 0.3)',
                      color: '#60a5fa',
                      borderRadius: '8px',
                      padding: '5px 10px',
                      fontSize: '11px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <Sparkles size={11} color="#60a5fa" />
                    <span>Ask AI</span>
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Email Reader Drawer / Modal */}
      {selectedEmail && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(8px)',
            zIndex: 110,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
          }}
          onClick={() => setSelectedEmail(null)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '680px',
              background: '#16161b',
              border: '1px solid rgba(0, 120, 212, 0.3)',
              borderRadius: '20px',
              padding: '24px',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6)',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              maxHeight: '85vh',
              overflowY: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
              <div>
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: '#0078d4',
                    background: 'rgba(0, 120, 212, 0.15)',
                    padding: '2px 8px',
                    borderRadius: '6px',
                  }}
                >
                  Outlook Message
                </span>
                <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#f3f4f6', margin: '8px 0 0 0' }}>
                  {selectedEmail.subject}
                </h2>
              </div>
              <button
                onClick={() => setSelectedEmail(null)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#9ca3af',
                  cursor: 'pointer',
                  padding: '4px',
                }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '12px', color: '#9ca3af', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '12px' }}>
              <div><strong>From:</strong> {selectedEmail.from} &lt;{selectedEmail.from_email}&gt;</div>
              {selectedEmail.to && selectedEmail.to.length > 0 && (
                <div><strong>To:</strong> {selectedEmail.to.join(', ')}</div>
              )}
              {selectedEmail.receivedDateTime && (
                <div><strong>Date:</strong> {new Date(selectedEmail.receivedDateTime).toLocaleString()}</div>
              )}
            </div>

            <div
              style={{
                fontSize: '13px',
                color: '#e5e7eb',
                lineHeight: 1.6,
                whiteSpace: 'pre-wrap',
                padding: '8px 0',
                minHeight: '120px',
              }}
            >
              {selectedEmail.body || selectedEmail.bodyPreview}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => {
                    handleReplyDirectly(selectedEmail);
                    setSelectedEmail(null);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '8px 14px',
                    borderRadius: '10px',
                    background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                    border: 'none',
                    color: '#fff',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  <Reply size={13} />
                  <span>Reply</span>
                </button>

                <button
                  onClick={() => {
                    onAskAgent(`Please draft a professional reply to this Outlook email from ${selectedEmail.from} regarding "${selectedEmail.subject}"`);
                    setSelectedEmail(null);
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '8px 14px',
                    borderRadius: '10px',
                    background: 'rgba(168, 85, 247, 0.15)',
                    border: '1px solid rgba(168, 85, 247, 0.3)',
                    color: '#c084fc',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  <Sparkles size={13} />
                  <span>Draft Reply with AI</span>
                </button>
              </div>

              <button
                onClick={() => setSelectedEmail(null)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: '#9ca3af',
                  fontSize: '12px',
                  cursor: 'pointer',
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Compose Email Modal */}
      {showCompose && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(8px)',
            zIndex: 110,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
          }}
          onClick={() => setShowCompose(false)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '600px',
              background: '#16161b',
              border: '1px solid rgba(0, 120, 212, 0.3)',
              borderRadius: '20px',
              padding: '24px',
              boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6)',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Send size={18} color="#0078d4" />
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f3f4f6', margin: 0 }}>
                  Compose Email (via Microsoft Outlook)
                </h3>
              </div>
              <button
                onClick={() => setShowCompose(false)}
                style={{ background: 'transparent', border: 'none', color: '#9ca3af', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            {sendStatus && (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: sendStatus.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  border: sendStatus.success ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(239, 68, 68, 0.3)',
                  color: sendStatus.success ? '#34d399' : '#f87171',
                  fontSize: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                {sendStatus.success ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                <span>{sendStatus.message}</span>
              </div>
            )}

            <form onSubmit={handleSendEmail} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '11px', color: '#9ca3af', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                  To (Recipient Email)
                </label>
                <input
                  type="email"
                  required
                  placeholder="colleague@example.com"
                  value={sendForm.to}
                  onChange={(e) => setSendForm({ ...sendForm, to: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#f3f4f6',
                    fontSize: '13px',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '11px', color: '#9ca3af', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                  Subject
                </label>
                <input
                  type="text"
                  required
                  placeholder="Meeting follow-up / Project status"
                  value={sendForm.subject}
                  onChange={(e) => setSendForm({ ...sendForm, subject: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#f3f4f6',
                    fontSize: '13px',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '11px', color: '#9ca3af', fontWeight: 600, display: 'block', marginBottom: '4px' }}>
                  Message Content
                </label>
                <textarea
                  required
                  rows={6}
                  placeholder="Type your message here..."
                  value={sendForm.body}
                  onChange={(e) => setSendForm({ ...sendForm, body: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#f3f4f6',
                    fontSize: '13px',
                    outline: 'none',
                    resize: 'vertical',
                    fontFamily: 'inherit',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '6px' }}>
                <button
                  type="button"
                  onClick={() => setShowCompose(false)}
                  style={{
                    padding: '9px 16px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#d1d5db',
                    fontSize: '12px',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={isSending}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '9px 18px',
                    borderRadius: '10px',
                    background: 'linear-gradient(135deg, #0078d4 0%, #0284c7 100%)',
                    border: 'none',
                    color: '#fff',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    boxShadow: '0 4px 14px rgba(0, 120, 212, 0.35)',
                  }}
                >
                  <Send size={13} />
                  <span>{isSending ? 'Sending via Outlook...' : 'Send Email'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
