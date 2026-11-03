import React, { useState, useEffect } from 'react';
import {
  Calendar as CalendarIcon,
  Clock,
  Video,
  Plus,
  RefreshCw,
  Sparkles,
  MapPin,
  Users,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { getApiUrl } from '../../config/api';

export default function CalendarView({ onAskAgent }) {
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [daysAhead, setDaysAhead] = useState(7);
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    summary: '',
    start_time: '',
    end_time: '',
    description: '',
    add_meet_link: true,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState(null);

  const fetchCalendar = async (days = daysAhead) => {
    setIsLoading(true);
    try {
      const res = await fetch(getApiUrl(`/api/google/calendar?days=${days}`));
      if (res.ok) {
        const data = await res.json();
        setEvents(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch calendar agenda', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCalendar(daysAhead);
  }, [daysAhead]);

  const handleCreateEvent = async (e) => {
    e.preventDefault();
    if (!createForm.summary || !createForm.start_time || !createForm.end_time) return;

    setIsSubmitting(true);
    setSubmitMessage(null);
    try {
      const res = await fetch(getApiUrl('/api/google/calendar/create'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(createForm),
      });
      if (res.ok) {
        setSubmitMessage({ type: 'success', text: 'Meeting scheduled successfully!' });
        setCreateForm({
          summary: '',
          start_time: '',
          end_time: '',
          description: '',
          add_meet_link: true,
        });
        setTimeout(() => {
          setShowCreate(false);
          setSubmitMessage(null);
          fetchCalendar(daysAhead);
        }, 1500);
      } else {
        const err = await res.json();
        setSubmitMessage({ type: 'error', text: `Failed: ${err.detail || 'Could not schedule'}` });
      }
    } catch (err) {
      setSubmitMessage({ type: 'error', text: `Error: ${err.message}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatEventDate = (dtStr) => {
    if (!dtStr) return '';
    try {
      const d = new Date(dtStr);
      return d.toLocaleDateString(undefined, {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dtStr;
    }
  };

  const formatEventTime = (dtStr) => {
    if (!dtStr) return '';
    try {
      const d = new Date(dtStr);
      return d.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dtStr;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Header Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          {[
            { label: 'Next 3 Days', days: 3 },
            { label: 'Next 7 Days', days: 7 },
            { label: 'Next 14 Days', days: 14 },
            { label: 'Next 30 Days', days: 30 },
          ].map((item) => (
            <button
              key={item.days}
              onClick={() => setDaysAhead(item.days)}
              style={{
                padding: '6px 14px',
                borderRadius: '20px',
                background: daysAhead === item.days ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                border: daysAhead === item.days ? '1px solid rgba(59, 130, 246, 0.5)' : '1px solid rgba(255, 255, 255, 0.06)',
                color: daysAhead === item.days ? '#60a5fa' : '#9ca3af',
                fontSize: '12px',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => fetchCalendar(daysAhead)}
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
            onClick={() => setShowCreate(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '10px 16px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              border: 'none',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
            }}
          >
            <Plus size={15} />
            <span>Schedule Meeting</span>
          </button>
        </div>
      </div>

      {/* Events List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {isLoading && events.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af', fontSize: '13px' }}>
            Fetching upcoming agenda from Google Calendar...
          </div>
        ) : events.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280', fontSize: '13px' }}>
            No upcoming events scheduled in the next {daysAhead} days.
          </div>
        ) : (
          events.map((ev) => {
            const hasMeet = Boolean(ev.hangoutLink);
            return (
              <div
                key={ev.id}
                style={{
                  padding: '16px',
                  borderRadius: '16px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                  transition: 'background 0.15s',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div
                      style={{
                        width: '38px',
                        height: '38px',
                        borderRadius: '12px',
                        background: hasMeet ? 'rgba(59, 130, 246, 0.15)' : 'rgba(168, 85, 247, 0.15)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      {hasMeet ? <Video size={18} color="#60a5fa" /> : <CalendarIcon size={18} color="#c084fc" />}
                    </div>
                    <div>
                      <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#f3f4f6' }}>
                        {ev.summary || '(Untitled Event)'}
                      </h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '2px', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '12px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={12} />
                          {formatEventDate(ev.start)} • {formatEventTime(ev.start)} – {formatEventTime(ev.end)}
                        </span>
                        {ev.location && (
                          <span style={{ fontSize: '12px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <MapPin size={12} /> {ev.location}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {ev.htmlLink && (
                    <a
                      href={ev.htmlLink}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '11px',
                        color: '#9ca3af',
                        textDecoration: 'none',
                        padding: '4px 8px',
                        borderRadius: '6px',
                        background: 'rgba(255, 255, 255, 0.04)',
                      }}
                    >
                      Open Calendar <ExternalLink size={11} />
                    </a>
                  )}
                </div>

                {ev.description && (
                  <p style={{ fontSize: '12px', color: '#9ca3af', lineHeight: 1.4, margin: '2px 0 0 0' }}>
                    {ev.description}
                  </p>
                )}

                {ev.attendees && ev.attendees.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                    <Users size={12} color="#6b7280" />
                    {ev.attendees.map((att, i) => (
                      <span
                        key={i}
                        style={{
                          fontSize: '11px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          color: '#d1d5db',
                          padding: '2px 8px',
                          borderRadius: '6px',
                        }}
                      >
                        {att}
                      </span>
                    ))}
                  </div>
                )}

                {/* Action footer */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', marginTop: '4px', flexWrap: 'wrap' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => onAskAgent(`Prepare a meeting briefing for: "${ev.summary}" at ${ev.start}. Details: ${ev.description || 'none'}`)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px',
                        padding: '5px 10px',
                        borderRadius: '8px',
                        background: 'rgba(168, 85, 247, 0.1)',
                        border: '1px solid rgba(168, 85, 247, 0.25)',
                        color: '#c084fc',
                        fontSize: '11px',
                        fontWeight: 500,
                        cursor: 'pointer',
                      }}
                    >
                      <Sparkles size={12} /> Prep with AI
                    </button>

                    <button
                      onClick={() => onAskAgent(`Check my schedule conflicts for "${ev.summary}" on ${ev.start}`)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px',
                        padding: '5px 10px',
                        borderRadius: '8px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        color: '#d1d5db',
                        fontSize: '11px',
                        cursor: 'pointer',
                      }}
                    >
                      Check Conflicts
                    </button>
                  </div>

                  {hasMeet && (
                    <a
                      href={ev.hangoutLink}
                      target="_blank"
                      rel="noreferrer"
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 12px',
                        borderRadius: '8px',
                        background: 'rgba(59, 130, 246, 0.15)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        color: '#60a5fa',
                        fontSize: '12px',
                        fontWeight: 600,
                        textDecoration: 'none',
                      }}
                    >
                      <Video size={13} /> Join Google Meet
                    </a>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Schedule Meeting Modal */}
      {showCreate && (
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
          onClick={() => setShowCreate(false)}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '520px',
              background: '#16161b',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '20px',
              padding: '24px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f3f4f6', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CalendarIcon size={16} color="#3b82f6" /> Schedule New Meeting
            </h3>

            {submitMessage && (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: submitMessage.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                  color: submitMessage.type === 'success' ? '#34d399' : '#f87171',
                  fontSize: '12px',
                  marginBottom: '14px',
                }}
              >
                {submitMessage.text}
              </div>
            )}

            <form onSubmit={handleCreateEvent} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#9ca3af' }}>Title / Summary:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. AI Architecture Review"
                  value={createForm.summary}
                  onChange={(e) => setCreateForm({ ...createForm, summary: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#f3f4f6',
                    fontSize: '13px',
                    outline: 'none',
                    marginTop: '4px',
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 600, color: '#9ca3af' }}>Start Time:</label>
                  <input
                    type="datetime-local"
                    required
                    value={createForm.start_time}
                    onChange={(e) => setCreateForm({ ...createForm, start_time: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '8px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      color: '#f3f4f6',
                      fontSize: '12px',
                      outline: 'none',
                      marginTop: '4px',
                    }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 600, color: '#9ca3af' }}>End Time:</label>
                  <input
                    type="datetime-local"
                    required
                    value={createForm.end_time}
                    onChange={(e) => setCreateForm({ ...createForm, end_time: e.target.value })}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '8px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      color: '#f3f4f6',
                      fontSize: '12px',
                      outline: 'none',
                      marginTop: '4px',
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#9ca3af' }}>Description / Agenda:</label>
                <textarea
                  rows={3}
                  placeholder="Add notes, agenda items..."
                  value={createForm.description}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#f3f4f6',
                    fontSize: '13px',
                    outline: 'none',
                    marginTop: '4px',
                    resize: 'vertical',
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                <input
                  type="checkbox"
                  id="meet-link"
                  checked={createForm.add_meet_link}
                  onChange={(e) => setCreateForm({ ...createForm, add_meet_link: e.target.checked })}
                  style={{ accentColor: '#3b82f6', width: '16px', height: '16px' }}
                />
                <label htmlFor="meet-link" style={{ fontSize: '12px', color: '#d1d5db', cursor: 'pointer' }}>
                  Generate Google Meet video link
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '12px' }}>
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  style={{ padding: '8px 14px', borderRadius: '8px', background: 'transparent', border: '1px solid rgba(255, 255, 255, 0.1)', color: '#9ca3af', fontSize: '12px', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  style={{ padding: '8px 18px', borderRadius: '8px', background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', border: 'none', color: '#fff', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
                >
                  {isSubmitting ? 'Scheduling...' : 'Save to Google Calendar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
