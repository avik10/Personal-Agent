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
  X
} from 'lucide-react';
import { getApiUrl } from '../../config/api';

export default function GmailView({ onAskAgent }) {
  const [emails, setEmails] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [showCompose, setShowCompose] = useState(false);
  const [sendForm, setSendForm] = useState({ to: '', subject: '', body: '' });
  const [isSending, setIsSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(null);

  const handleReplyDirectly = (msg) => {
    const rawFrom = msg.from || '';
    const emailMatch = rawFrom.match(/<([^>]+)>/);
    const targetEmail = emailMatch ? emailMatch[1].trim() : rawFrom.trim();
    const cleanSubject = msg.subject || '';
    const replySubject = cleanSubject.toLowerCase().startsWith('re:') ? cleanSubject : `Re: ${cleanSubject}`;

    setSendForm({
      to: targetEmail,
      subject: replySubject,
      body: `\n\n--- On ${msg.date || 'recent'}, ${rawFrom} wrote:\n> ${msg.snippet || ''}`,
    });
    setSendSuccess(null);
    setShowCompose(true);
  };

  const fetchEmails = async (query = '') => {
    setIsLoading(true);
    try {
      const qParam = query ? `?q=${encodeURIComponent(query)}&max_results=12` : '?max_results=12';
      const res = await fetch(getApiUrl(`/api/google/emails${qParam}`));
      if (res.ok) {
        const data = await res.json();
        setEmails(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch emails', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchEmails(searchQuery);
  };

  const handleFilterClick = (filter, queryStr) => {
    setActiveFilter(filter);
    setSearchQuery(queryStr);
    fetchEmails(queryStr);
  };

  const handleSendEmail = async (e) => {
    e.preventDefault();
    const cleanTo = (sendForm.to || '').trim();
    const cleanSubject = (sendForm.subject || '').trim();
    const cleanBody = (sendForm.body || '').trim();

    if (!cleanTo || !cleanSubject) {
      setSendSuccess('Please provide both recipient email and subject line.');
      return;
    }

    setIsSending(true);
    setSendSuccess(null);
    try {
      const res = await fetch(getApiUrl('/api/google/emails/send'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: cleanTo,
          subject: cleanSubject,
          body: cleanBody,
        }),
      });
      if (res.ok) {
        const result = await res.json().catch(() => ({}));
        const sentTo = result.to || cleanTo;
        setSendSuccess(`✓ Email successfully sent to ${sentTo}!`);
        setSendForm({ to: '', subject: '', body: '' });
        setTimeout(() => {
          setShowCompose(false);
          setSendSuccess(null);
          fetchEmails();
        }, 2200);
      } else {
        const err = await res.json().catch(() => ({}));
        setSendSuccess(`Failed: ${err.detail || 'Could not send email'}`);
      }
    } catch (err) {
      setSendSuccess(`Error: ${err.message}`);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Controls: Search & Compose */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
        <form onSubmit={handleSearch} style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search size={16} color="#9ca3af" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search emails (e.g. is:unread, from:google)..."
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

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => fetchEmails(searchQuery)}
            disabled={isLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '10px 14px',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#d1d5db',
              fontSize: '13px',
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>

          <button
            onClick={() => setShowCompose(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '10px 16px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              border: 'none',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(239, 68, 68, 0.3)',
            }}
          >
            <Send size={14} />
            <span>Compose Email</span>
          </button>
        </div>
      </div>

      {/* Filter Chips */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto' }}>
        {[
          { id: 'all', label: 'All Mail', q: '' },
          { id: 'unread', label: 'Unread Only', q: 'is:unread' },
          { id: 'starred', label: 'Starred', q: 'is:starred' },
          { id: 'attachments', label: 'With Attachments', q: 'has:attachment' },
        ].map((f) => (
          <button
            key={f.id}
            onClick={() => handleFilterClick(f.id, f.q)}
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              background: activeFilter === f.id ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.04)',
              border: activeFilter === f.id ? '1px solid rgba(239, 68, 68, 0.5)' : '1px solid rgba(255, 255, 255, 0.06)',
              color: activeFilter === f.id ? '#f87171' : '#9ca3af',
              fontSize: '12px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Email List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {isLoading && emails.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af', fontSize: '13px' }}>
            Loading emails from Gmail...
          </div>
        ) : emails.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280', fontSize: '13px' }}>
            No messages found for this filter.
          </div>
        ) : (
          emails.map((msg) => {
            const isUnread = msg.labelIds?.includes('UNREAD');
            return (
              <div
                key={msg.id}
                style={{
                  padding: '16px',
                  borderRadius: '14px',
                  background: isUnread ? 'rgba(239, 68, 68, 0.05)' : 'rgba(255, 255, 255, 0.03)',
                  border: isUnread ? '1px solid rgba(239, 68, 68, 0.25)' : '1px solid rgba(255, 255, 255, 0.06)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  transition: 'background 0.15s',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: isUnread ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.08)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <User size={14} color={isUnread ? '#f87171' : '#9ca3af'} />
                    </div>
                    <span style={{ fontSize: '13px', fontWeight: isUnread ? 700 : 500, color: '#f3f4f6', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {msg.from}
                    </span>
                    {isUnread && (
                      <span style={{ fontSize: '10px', background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', padding: '1px 6px', borderRadius: '6px', fontWeight: 600 }}>
                        UNREAD
                      </span>
                    )}
                  </div>
                  <span style={{ fontSize: '11px', color: '#9ca3af', flexShrink: 0 }}>
                    {msg.date ? new Date(msg.date).toLocaleDateString() : ''}
                  </span>
                </div>

                <h4 style={{ fontSize: '14px', fontWeight: isUnread ? 700 : 600, color: '#f3f4f6' }}>
                  {msg.subject || '(No Subject)'}
                </h4>

                <p style={{ fontSize: '12px', color: '#9ca3af', lineHeight: 1.4, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                  {msg.snippet}
                </p>

                {/* AI Actions */}
                <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                  <button
                    onClick={() => onAskAgent(`Summarize this email from "${msg.from}" with subject "${msg.subject}": ${msg.snippet}`)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px',
                      padding: '4px 10px',
                      borderRadius: '8px',
                      background: 'rgba(168, 85, 247, 0.1)',
                      border: '1px solid rgba(168, 85, 247, 0.25)',
                      color: '#c084fc',
                      fontSize: '11px',
                      fontWeight: 500,
                      cursor: 'pointer',
                    }}
                  >
                    <Sparkles size={12} /> Summarize with AI
                  </button>

                  <button
                    onClick={() => handleReplyDirectly(msg)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px',
                      padding: '4px 10px',
                      borderRadius: '8px',
                      background: 'rgba(239, 68, 68, 0.12)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      color: '#f87171',
                      fontSize: '11px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    <Reply size={12} /> Reply
                  </button>

                  <button
                    onClick={() => onAskAgent(`Draft a polite professional reply to this email from "${msg.from}" with subject "${msg.subject}".`)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px',
                      padding: '4px 10px',
                      borderRadius: '8px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      color: '#d1d5db',
                      fontSize: '11px',
                      cursor: 'pointer',
                    }}
                  >
                    Draft Reply
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Compose Email Modal */}
      {showCompose && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(6px)',
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
              maxWidth: '540px',
              background: '#16161b',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '20px',
              padding: '24px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Send size={16} color="#ef4444" /> Compose & Send Email
                </h3>
                <p style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>
                  Delivering live from your connected Gmail account
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowCompose(false)}
                style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', padding: '4px' }}
                title="Close"
              >
                <X size={18} />
              </button>
            </div>

            {sendSuccess && (
              <div style={{ padding: '10px 14px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', fontSize: '12px', marginBottom: '14px', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
                {sendSuccess}
              </div>
            )}

            <form onSubmit={handleSendEmail} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <label style={{ fontSize: '11px', fontWeight: 600, color: '#d1d5db' }}>To (Recipient Email Address):</label>
                  <button
                    type="button"
                    onClick={() => setSendForm((prev) => ({ ...prev, to: 'avik.bhattacharjya28@gmail.com' }))}
                    style={{
                      fontSize: '10px',
                      color: '#60a5fa',
                      background: 'rgba(59, 130, 246, 0.1)',
                      border: '1px solid rgba(59, 130, 246, 0.25)',
                      borderRadius: '6px',
                      padding: '2px 8px',
                      cursor: 'pointer',
                      fontWeight: 500,
                    }}
                  >
                    + Send test to myself
                  </button>
                </div>
                <input
                  type="email"
                  required
                  placeholder="Enter recipient email (e.g. colleague@company.com)"
                  value={sendForm.to}
                  onChange={(e) => setSendForm({ ...sendForm, to: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#f3f4f6',
                    fontSize: '13px',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#d1d5db' }}>Subject:</label>
                <input
                  type="text"
                  required
                  placeholder="Enter subject line..."
                  value={sendForm.subject}
                  onChange={(e) => setSendForm({ ...sendForm, subject: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#f3f4f6',
                    fontSize: '13px',
                    outline: 'none',
                    marginTop: '4px',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#d1d5db' }}>Message Body:</label>
                <textarea
                  rows={6}
                  required
                  placeholder="Write your email message here..."
                  value={sendForm.body}
                  onChange={(e) => setSendForm({ ...sendForm, body: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#f3f4f6',
                    fontSize: '13px',
                    outline: 'none',
                    marginTop: '4px',
                    resize: 'vertical',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
                <button
                  type="button"
                  onClick={() => setShowCompose(false)}
                  style={{ padding: '8px 14px', borderRadius: '8px', background: 'transparent', border: '1px solid rgba(255, 255, 255, 0.1)', color: '#9ca3af', fontSize: '12px', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSending}
                  style={{ padding: '8px 18px', borderRadius: '8px', background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', border: 'none', color: '#fff', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
                >
                  {isSending ? 'Sending...' : 'Send Message'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
