import React from 'react';
import { Menu, Sparkles, Folder } from 'lucide-react';

export default function Header({
  onToggleSidebar,
  systemStatus,
  activeView
}) {
  const modelName = systemStatus?.backend_model || 'qwen/qwen3.8-27b';

  return (
    <header
      style={{
        height: '60px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 20px',
        background: 'rgba(14, 14, 17, 0.85)',
        backdropFilter: 'blur(12px)',
        zIndex: 30,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <button
          onClick={onToggleSidebar}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#9ca3af',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#fff')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#9ca3af')}
        >
          <Menu size={20} />
        </button>

        {/* Current Active View Title */}
        {activeView === 'google' ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                padding: '5px',
                borderRadius: '8px',
                background: 'rgba(66, 133, 244, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Folder size={15} color="#60a5fa" />
            </div>
            <span style={{ fontSize: '14px', fontWeight: 600, color: '#f3f4f6' }}>
              Google Workspace Bucket
            </span>
          </div>
        ) : activeView === 'microsoft' ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                padding: '5px',
                borderRadius: '8px',
                background: 'rgba(0, 120, 212, 0.18)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Folder size={15} color="#0078d4" />
            </div>
            <span style={{ fontSize: '14px', fontWeight: 600, color: '#f3f4f6' }}>
              Microsoft Bucket
            </span>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: 600, color: '#f3f4f6' }}>
              Chat Studio
            </span>
          </div>
        )}
      </div>

      {/* Right Side: Model Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 12px',
            borderRadius: '16px',
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid rgba(255, 255, 255, 0.07)',
          }}
        >
          <Sparkles size={12} color="#a855f7" />
          <span style={{ fontSize: '11px', color: '#d1d5db', fontWeight: 500 }}>
            {modelName}
          </span>
        </div>
      </div>
    </header>
  );
}
