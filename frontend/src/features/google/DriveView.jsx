import React, { useState, useEffect } from 'react';
import {
  HardDrive,
  Search,
  RefreshCw,
  Sparkles,
  FileText,
  FileSpreadsheet,
  FileCode,
  File,
  Folder,
  ExternalLink,
  Clock,
  Download
} from 'lucide-react';
import { getApiUrl } from '../../config/api';

export default function DriveView({ onAskAgent }) {
  const [files, setFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');

  const fetchFiles = async (query = '') => {
    setIsLoading(true);
    try {
      const qParam = query ? `?query=${encodeURIComponent(query)}&page_size=20` : '?page_size=20';
      const res = await fetch(getApiUrl(`/api/google/drive${qParam}`));
      if (res.ok) {
        const data = await res.json();
        setFiles(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      console.error('Failed to fetch Drive files', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchFiles(searchQuery);
  };

  const handleFilterClick = (filter, queryStr) => {
    setTypeFilter(filter);
    setSearchQuery(queryStr);
    fetchFiles(queryStr);
  };

  const getFileIcon = (mimeType = '') => {
    if (mimeType.includes('folder')) {
      return <Folder size={20} color="#fbbf24" />;
    }
    if (mimeType.includes('document') || mimeType.includes('text') || mimeType.includes('pdf')) {
      return <FileText size={20} color="#60a5fa" />;
    }
    if (mimeType.includes('spreadsheet') || mimeType.includes('csv')) {
      return <FileSpreadsheet size={20} color="#34d399" />;
    }
    if (mimeType.includes('json') || mimeType.includes('script')) {
      return <FileCode size={20} color="#c084fc" />;
    }
    return <File size={20} color="#9ca3af" />;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '--';
    const num = parseInt(bytes, 10);
    if (isNaN(num)) return '--';
    if (num < 1024) return `${num} B`;
    if (num < 1024 * 1024) return `${(num / 1024).toFixed(1)} KB`;
    return `${(num / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatModifiedTime = (timeStr) => {
    if (!timeStr) return '';
    try {
      return new Date(timeStr).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return timeStr;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Controls: Search & Refresh */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
        <form onSubmit={handleSearch} style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search size={16} color="#9ca3af" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Google Drive files..."
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

        <button
          onClick={() => fetchFiles(searchQuery)}
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
      </div>

      {/* Filter Chips */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto' }}>
        {[
          { id: 'all', label: 'All Files', q: '' },
          { id: 'docs', label: 'Docs', q: "mimeType contains 'document'" },
          { id: 'sheets', label: 'Sheets', q: "mimeType contains 'spreadsheet'" },
          { id: 'folders', label: 'Folders', q: "mimeType = 'application/vnd.google-apps.folder'" },
        ].map((f) => (
          <button
            key={f.id}
            onClick={() => handleFilterClick(f.id, f.q)}
            style={{
              padding: '6px 14px',
              borderRadius: '20px',
              background: typeFilter === f.id ? 'rgba(52, 211, 153, 0.2)' : 'rgba(255, 255, 255, 0.04)',
              border: typeFilter === f.id ? '1px solid rgba(52, 211, 153, 0.5)' : '1px solid rgba(255, 255, 255, 0.06)',
              color: typeFilter === f.id ? '#34d399' : '#9ca3af',
              fontSize: '12px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Files Grid */}
      {isLoading && files.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af', fontSize: '13px' }}>
          Accessing Google Drive files...
        </div>
      ) : files.length === 0 ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280', fontSize: '13px' }}>
          No files found in Google Drive.
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '14px',
          }}
        >
          {files.map((file) => (
            <div
              key={file.id}
              style={{
                padding: '16px',
                borderRadius: '16px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '12px',
                transition: 'border 0.2s, background 0.2s',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div
                      style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '10px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      {getFileIcon(file.mimeType)}
                    </div>
                    <div style={{ overflow: 'hidden' }}>
                      <h4
                        title={file.name}
                        style={{
                          fontSize: '13px',
                          fontWeight: 600,
                          color: '#f3f4f6',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {file.name}
                      </h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '2px' }}>
                        <span style={{ fontSize: '11px', color: '#9ca3af' }}>
                          {formatFileSize(file.size)}
                        </span>
                        {file.modifiedTime && (
                          <span style={{ fontSize: '11px', color: '#6b7280' }}>
                            • {formatModifiedTime(file.modifiedTime)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {file.webViewLink && (
                    <a
                      href={file.webViewLink}
                      target="_blank"
                      rel="noreferrer"
                      title="Open in Google Drive"
                      style={{
                        padding: '6px',
                        borderRadius: '8px',
                        background: 'rgba(255, 255, 255, 0.04)',
                        color: '#9ca3af',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textDecoration: 'none',
                        flexShrink: 0,
                      }}
                    >
                      <ExternalLink size={13} />
                    </a>
                  )}
                </div>
              </div>

              {/* AI Actions */}
              <div style={{ display: 'flex', gap: '6px', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <button
                  onClick={() => onAskAgent(`Summarize Google Drive document "${file.name}" (ID: ${file.id})`)}
                  style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '4px',
                    padding: '6px 10px',
                    borderRadius: '8px',
                    background: 'rgba(168, 85, 247, 0.1)',
                    border: '1px solid rgba(168, 85, 247, 0.25)',
                    color: '#c084fc',
                    fontSize: '11px',
                    fontWeight: 500,
                    cursor: 'pointer',
                  }}
                >
                  <Sparkles size={11} /> Summarize with AI
                </button>
                <button
                  onClick={() => onAskAgent(`Extract key insights and action points from Drive file "${file.name}"`)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '6px 10px',
                    borderRadius: '8px',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    color: '#d1d5db',
                    fontSize: '11px',
                    cursor: 'pointer',
                  }}
                >
                  Insights
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
