import React, { useRef, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';

export default function InputBar({
  input,
  setInput,
  onSendMessage,
  isLoading
}) {
  const textareaRef = useRef(null);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && input.trim()) {
        onSendMessage(input);
      }
    }
  };

  return (
    <div
      style={{
        padding: '12px 20px 24px 20px',
        maxWidth: '860px',
        width: '100%',
        margin: '0 auto',
      }}
    >
      {/* Floating Gemini Input Container (No clickable query pills) */}
      <div
        className="gemini-input-container"
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          padding: '14px 16px',
          gap: '10px',
        }}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything or describe what you need..."
          rows={1}
          disabled={isLoading}
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: '#f3f4f6',
            fontSize: '14px',
            fontFamily: 'inherit',
            resize: 'none',
            maxHeight: '180px',
            lineHeight: '1.5',
            padding: '2px 0',
          }}
        />

        <button
          onClick={() => onSendMessage(input)}
          disabled={isLoading || !input.trim()}
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background:
              input.trim() && !isLoading
                ? 'linear-gradient(135deg, #a855f7 0%, #3b82f6 100%)'
                : 'rgba(255, 255, 255, 0.08)',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
            transition: 'all 0.2s',
            boxShadow:
              input.trim() && !isLoading ? '0 2px 10px rgba(168, 85, 247, 0.4)' : 'none',
            flexShrink: 0,
          }}
        >
          <ArrowUp
            size={18}
            color={input.trim() && !isLoading ? '#ffffff' : '#6b7280'}
          />
        </button>
      </div>

      <div
        style={{
          textAlign: 'center',
          marginTop: '8px',
          fontSize: '11px',
          color: '#6b7280',
        }}
      >
        Personal AI Agent connects directly to local Ollama and live specialized multi-agents.
      </div>
    </div>
  );
}
