import React, { useState, useEffect } from 'react';
import {
  CheckSquare,
  Square,
  Search,
  RefreshCw,
  Plus,
  Sparkles,
  Calendar as CalendarIcon,
  Clock,
  Trash2,
  FileText,
  CheckCircle2,
  AlertCircle,
  X
} from 'lucide-react';
import { getApiUrl } from '../../config/api';

export default function NotesView({ onAskAgent }) {
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('all'); // 'all' | 'pending' | 'completed' | 'notes'
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({ title: '', notes: '', due_date: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  const fetchNotes = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(getApiUrl('/api/google/notes?show_completed=true&max_results=50'));
      if (res.ok) {
        const data = await res.json();
        setItems(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch notes & tasks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const handleCreateNote = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) return;

    setIsSubmitting(true);
    setStatusMessage(null);

    try {
      const payload = {
        title: formData.title.trim(),
        notes: formData.notes.trim() || null,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null,
      };

      const res = await fetch(getApiUrl('/api/google/notes/create'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setStatusMessage({ type: 'success', text: '✓ Note/Task saved to Google!' });
        setFormData({ title: '', notes: '', due_date: '' });
        setTimeout(() => {
          setShowCreateModal(false);
          setStatusMessage(null);
          fetchNotes();
        }, 1200);
      } else {
        const err = await res.json().catch(() => ({}));
        setStatusMessage({ type: 'error', text: `Failed: ${err.detail || 'Could not save note'}` });
      }
    } catch (err) {
      setStatusMessage({ type: 'error', text: `Error: ${err.message}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleComplete = async (item) => {
    if (item.status === 'completed') return; // Already completed

    try {
      const res = await fetch(getApiUrl(`/api/google/notes/${encodeURIComponent(item.id)}/complete`), {
        method: 'POST',
      });
      if (res.ok) {
        setItems((prev) =>
          prev.map((i) => (i.id === item.id ? { ...i, status: 'completed' } : i))
        );
      }
    } catch (err) {
      console.error('Failed to complete note:', err);
    }
  };

  const handleDelete = async (itemId) => {
    try {
      const res = await fetch(getApiUrl(`/api/google/notes/${encodeURIComponent(itemId)}`), {
        method: 'DELETE',
      });
      if (res.ok) {
        setItems((prev) => prev.filter((i) => i.id !== itemId));
      }
    } catch (err) {
      console.error('Failed to delete note:', err);
    }
  };

  // Filtered items based on activeFilter and searchQuery
  const filteredItems = items.filter((item) => {
    const matchesSearch =
      (item.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.notes || '').toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (activeFilter === 'pending') {
      return item.status !== 'completed';
    }
    if (activeFilter === 'completed') {
      return item.status === 'completed';
    }
    if (activeFilter === 'notes') {
      return Boolean(item.notes && item.notes.trim().length > 0);
    }
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Google Account Sync Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '12px 16px',
          borderRadius: '12px',
          background: 'rgba(251, 191, 36, 0.08)',
          border: '1px solid rgba(251, 191, 36, 0.25)',
          color: '#fbbf24',
          fontSize: '12px',
          lineHeight: '1.5',
        }}
      >
        <CheckSquare size={16} style={{ flexShrink: 0 }} />
        <span>
          <strong>Google Workspace Account Sync:</strong> Notes and to-dos are stored securely in your real Google Account via <strong>Google Tasks</strong>. They appear automatically in your <strong>Gmail right-sidebar (Tasks checkmark)</strong>, <strong>Google Calendar</strong> (calendar.google.com), and the <strong>Google Tasks mobile app</strong>.
        </span>
      </div>

      {/* Search & Actions Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search
            size={16}
            color="#9ca3af"
            style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }}
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Google Notes & Tasks..."
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
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={fetchNotes}
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
            onClick={() => {
              setShowCreateModal(true);
              setStatusMessage(null);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '10px 16px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              border: 'none',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)',
            }}
          >
            <Plus size={16} />
            <span>New Note / Task</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto' }}>
        {[
          { id: 'all', label: `All Items (${items.length})` },
          { id: 'pending', label: `Pending Tasks (${items.filter((i) => i.status !== 'completed').length})` },
          { id: 'completed', label: `Completed (${items.filter((i) => i.status === 'completed').length})` },
          { id: 'notes', label: `Detailed Notes (${items.filter((i) => Boolean(i.notes && i.notes.trim())).length})` },
        ].map((filter) => (
          <button
            key={filter.id}
            onClick={() => setActiveFilter(filter.id)}
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              background: activeFilter === filter.id ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255, 255, 255, 0.04)',
              border: activeFilter === filter.id ? '1px solid rgba(245, 158, 11, 0.5)' : '1px solid rgba(255, 255, 255, 0.06)',
              color: activeFilter === filter.id ? '#fbbf24' : '#9ca3af',
              fontSize: '12px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Notes & Tasks Cards Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {isLoading && items.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af', fontSize: '13px' }}>
            Loading notes and tasks from Google...
          </div>
        ) : filteredItems.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280', fontSize: '13px' }}>
            No notes or tasks found matching this view. Click "New Note / Task" to create one!
          </div>
        ) : (
          filteredItems.map((item) => {
            const isCompleted = item.status === 'completed';
            return (
              <div
                key={item.id}
                style={{
                  padding: '16px',
                  borderRadius: '14px',
                  background: isCompleted ? 'rgba(255, 255, 255, 0.02)' : 'rgba(245, 158, 11, 0.03)',
                  border: isCompleted ? '1px solid rgba(255, 255, 255, 0.05)' : '1px solid rgba(245, 158, 11, 0.2)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: '14px',
                  transition: 'background 0.15s',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', flex: 1 }}>
                  {/* Complete Checkbox */}
                  <button
                    onClick={() => handleToggleComplete(item)}
                    title={isCompleted ? 'Completed' : 'Click to complete'}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: '2px',
                      cursor: isCompleted ? 'default' : 'pointer',
                      color: isCompleted ? '#10b981' : '#9ca3af',
                      marginTop: '2px',
                    }}
                  >
                    {isCompleted ? <CheckSquare size={18} color="#10b981" /> : <Square size={18} />}
                  </button>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span
                        style={{
                          fontSize: '14px',
                          fontWeight: 600,
                          color: isCompleted ? '#6b7280' : '#f3f4f6',
                          textDecoration: isCompleted ? 'line-through' : 'none',
                        }}
                      >
                        {item.title}
                      </span>

                      {isCompleted ? (
                        <span
                          style={{
                            fontSize: '10px',
                            background: 'rgba(16, 185, 129, 0.15)',
                            color: '#34d399',
                            padding: '1px 6px',
                            borderRadius: '6px',
                            fontWeight: 600,
                          }}
                        >
                          DONE
                        </span>
                      ) : (
                        <span
                          style={{
                            fontSize: '10px',
                            background: 'rgba(245, 158, 11, 0.15)',
                            color: '#fbbf24',
                            padding: '1px 6px',
                            borderRadius: '6px',
                            fontWeight: 600,
                          }}
                        >
                          ACTIVE
                        </span>
                      )}
                    </div>

                    {item.notes && (
                      <p
                        style={{
                          fontSize: '12px',
                          color: '#9ca3af',
                          margin: 0,
                          whiteSpace: 'pre-wrap',
                          lineHeight: 1.5,
                        }}
                      >
                        {item.notes}
                      </p>
                    )}

                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginTop: '4px', flexWrap: 'wrap' }}>
                      <span
                        style={{
                          fontSize: '11px',
                          color: '#fbbf24',
                          background: 'rgba(251, 191, 36, 0.12)',
                          padding: '1px 8px',
                          borderRadius: '6px',
                          fontWeight: 500,
                        }}
                      >
                        {item.source === 'google_keep' ? 'Google Keep' : 'Google Tasks (Gmail/Calendar)'}
                      </span>

                      {item.due && (
                        <span style={{ fontSize: '11px', color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <CalendarIcon size={12} />
                          Due: {new Date(item.due).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        </span>
                      )}

                      {item.updated && (
                        <span style={{ fontSize: '11px', color: '#6b7280', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={12} />
                          {new Date(item.updated).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Card Actions */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    onClick={() => onAskAgent(`Regarding my note "${item.title}": summarize this item and suggest action steps`)}
                    title="Ask AI Agent about this item"
                    style={{
                      background: 'rgba(168, 85, 247, 0.1)',
                      border: '1px solid rgba(168, 85, 247, 0.25)',
                      color: '#c084fc',
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
                    <Sparkles size={12} />
                    <span>Ask Agent</span>
                  </button>

                  <button
                    onClick={() => handleDelete(item.id)}
                    title="Delete item"
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#6b7280',
                      cursor: 'pointer',
                      padding: '4px',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = '#ef4444')}
                    onMouseLeave={(e) => (e.currentTarget.style.color = '#6b7280')}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Create Note / Task Modal */}
      {showCreateModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px',
          }}
          onClick={() => setShowCreateModal(false)}
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FileText size={16} color="#f59e0b" /> Create Note or Task
                </h3>
                <p style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>
                  Saves directly to your connected Google Keep / Google Tasks account
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', padding: '4px' }}
                title="Close"
              >
                <X size={18} />
              </button>
            </div>

            {statusMessage && (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: statusMessage.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                  color: statusMessage.type === 'success' ? '#34d399' : '#f87171',
                  fontSize: '12px',
                  marginBottom: '14px',
                  border: statusMessage.type === 'success' ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid rgba(239, 68, 68, 0.25)',
                }}
              >
                {statusMessage.text}
              </div>
            )}

            <form onSubmit={handleCreateNote} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#d1d5db' }}>Title:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Weekly grocery checklist or Team retro notes"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
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
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#d1d5db' }}>Note Content / Details (Optional):</label>
                <textarea
                  rows={5}
                  placeholder="Type full note text, bullets, or instructions here..."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
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

              <div>
                <label style={{ fontSize: '11px', fontWeight: 600, color: '#d1d5db' }}>Due Date (Optional):</label>
                <input
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
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

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '8px',
                    background: 'transparent',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: '#9ca3af',
                    fontSize: '12px',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  style={{
                    padding: '8px 18px',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                    border: 'none',
                    color: '#fff',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  {isSubmitting ? 'Saving...' : 'Save to Google'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
