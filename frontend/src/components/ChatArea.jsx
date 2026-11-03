import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  User,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  Layers,
  Cpu,
  Zap,
  Clock,
  Activity,
  Mail
} from 'lucide-react';

function RealtimeAgentActivity() {
  const [step, setStep] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  const stages = [
    {
      title: 'Supervisor Intent Routing',
      detail: 'Analyzing query intent & decomposing sub-tasks...',
      badge: 'Router',
      color: '#c084fc',
      bg: 'rgba(192, 132, 252, 0.15)',
      icon: <Layers size={13} color="#c084fc" />,
    },
    {
      title: 'Specialist Agents Fan-Out',
      detail: 'Dispatching to Google MCP, Weather & Specialist agents in parallel...',
      badge: 'Multi-Agent',
      color: '#60a5fa',
      bg: 'rgba(96, 165, 250, 0.15)',
      icon: <Cpu size={13} color="#60a5fa" />,
    },
    {
      title: 'MCP Tools Execution',
      detail: 'Querying live Workspace APIs & executing tools behind the scenes...',
      badge: 'MCP Protocol',
      color: '#34d399',
      bg: 'rgba(52, 211, 153, 0.15)',
      icon: <Zap size={13} color="#34d399" />,
    },
    {
      title: 'Cross-Agent Synthesis',
      detail: 'Aggregating specialist outputs into a unified response...',
      badge: 'Synthesizer',
      color: '#f472b6',
      bg: 'rgba(244, 114, 182, 0.15)',
      icon: <Sparkles size={13} color="#f472b6" />,
    },
  ];

  // Advance step every 1.8 seconds
  useEffect(() => {
    const stageInterval = setInterval(() => {
      setStep((prev) => (prev + 1) % stages.length);
    }, 1800);
    return () => clearInterval(stageInterval);
  }, []);

  // Timer counter
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsed((prev) => prev + 0.1);
    }, 100);
    return () => clearInterval(timer);
  }, []);

  const current = stages[step];

  return (
    <div
      className="shimmer-active"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        padding: '14px 18px',
        borderRadius: '20px',
        background: 'rgba(22, 22, 27, 0.85)',
        border: '1px solid rgba(168, 85, 247, 0.3)',
        backdropFilter: 'blur(12px)',
        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4), 0 0 25px rgba(168, 85, 247, 0.15)',
        maxWidth: '520px',
        width: '100%',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
    >
      {/* Header Bar: Status Badge + Live Equalizer + Timer */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Animated Glowing Ring & Avatar */}
          <div
            style={{
              position: 'relative',
              width: '26px',
              height: '26px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #a855f7 0%, #3b82f6 50%, #ec4899 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 12px rgba(168, 85, 247, 0.5)',
            }}
          >
            <Activity size={14} color="#fff" />
          </div>

          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              color: current.color,
              background: current.bg,
              padding: '2px 8px',
              borderRadius: '6px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              transition: 'all 0.3s',
            }}
          >
            {current.icon}
            {current.badge}
          </span>
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#f3f4f6' }}>
            {current.title}
          </span>
        </div>

        {/* Live Equalizer + Elapsed Time */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '3px', height: '16px' }}>
            <span style={{ width: '3px', background: '#a855f7', borderRadius: '2px', animation: 'wave-bar 0.9s infinite ease-in-out 0s' }} />
            <span style={{ width: '3px', background: '#3b82f6', borderRadius: '2px', animation: 'wave-bar 0.9s infinite ease-in-out 0.2s' }} />
            <span style={{ width: '3px', background: '#10b981', borderRadius: '2px', animation: 'wave-bar 0.9s infinite ease-in-out 0.4s' }} />
            <span style={{ width: '3px', background: '#ec4899', borderRadius: '2px', animation: 'wave-bar 0.9s infinite ease-in-out 0.6s' }} />
          </div>
          <span style={{ fontSize: '11px', color: '#9ca3af', fontFamily: 'monospace', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <Clock size={11} /> {elapsed.toFixed(1)}s
          </span>
        </div>
      </div>

      {/* Real-time Detail Action */}
      <p style={{ fontSize: '12px', color: '#d1d5db', lineHeight: 1.4, margin: '2px 0 0 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span
          style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: current.color,
            boxShadow: `0 0 8px ${current.color}`,
            flexShrink: 0,
          }}
        />
        <span>{current.detail}</span>
      </p>

      {/* Multi-Agent Graph Node Progress Indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', paddingTop: '4px' }}>
        {stages.map((stg, i) => {
          const isActive = i === step;
          const isDone = i < step;
          return (
            <div key={i} style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '4px' }}>
              <div
                style={{
                  height: '3px',
                  flex: 1,
                  borderRadius: '2px',
                  background: isActive
                    ? stg.color
                    : isDone
                    ? 'rgba(255, 255, 255, 0.4)'
                    : 'rgba(255, 255, 255, 0.1)',
                  boxShadow: isActive ? `0 0 8px ${stg.color}` : 'none',
                  transition: 'all 0.3s ease',
                }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}

function renderInlineFormatting(text) {
  if (!text) return '';

  const parts = [];
  const regex = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let lastIdx = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIdx) {
      parts.push(text.substring(lastIdx, match.index));
    }
    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={match.index} style={{ color: '#f3f4f6', fontWeight: 600 }}>
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code
          key={match.index}
          style={{
            background: 'rgba(255, 255, 255, 0.1)',
            padding: '1px 5px',
            borderRadius: '4px',
            fontSize: '12px',
            color: '#c084fc',
          }}
        >
          {token.slice(1, -1)}
        </code>
      );
    }
    lastIdx = regex.lastIndex;
  }

  if (lastIdx < text.length) {
    parts.push(text.substring(lastIdx));
  }

  return parts.length > 0 ? parts : text;
}

function FormattedMessage({ content }) {
  if (!content) return null;

  // Unescape literal \r\n, \n, \t and remove zero-width non-joiners
  const cleanText = String(content)
    .replace(/\\r\\n/g, '\n')
    .replace(/\\n/g, '\n')
    .replace(/\\r/g, '\n')
    .replace(/\\t/g, '  ')
    .replace(/[\u200b-\u200f\ufeff\u202a-\u202e]/g, '')
    .replace(/\u00a0/g, ' ');

  // 1. Detect if content is a JSON email payload (raw or escaped)
  const trimmed = cleanText.trim();
  if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('{\n') && trimmed.endsWith('\n}'))) {
    try {
      const parsed = JSON.parse(trimmed);
      if (parsed && (parsed.headers || (parsed.snippet && parsed.id) || parsed.body)) {
        const headers = parsed.headers || {};
        const subject = headers.Subject || parsed.subject || '(No Subject)';
        const from = headers.From || parsed.from || 'Unknown';
        const to = headers.To || parsed.to || '';
        const date = headers.Date || parsed.date || '';
        const body = (parsed.body || parsed.snippet || '')
          .replace(/\\r\\n/g, '\n')
          .replace(/\\n/g, '\n')
          .replace(/[\u200b-\u200f\ufeff\u202a-\u202e]/g, '')
          .replace(/\u00a0/g, ' ')
          .replace(/\n{3,}/g, '\n\n')
          .trim();

        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                paddingBottom: '10px',
                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
              }}
            >
              <div
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '8px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <Mail size={15} color="#ef4444" />
              </div>
              <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#f3f4f6', margin: 0 }}>
                {subject}
              </h4>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'auto 1fr',
                gap: '4px 10px',
                fontSize: '12px',
                color: '#9ca3af',
                background: 'rgba(255, 255, 255, 0.02)',
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.04)',
              }}
            >
              <span style={{ fontWeight: 600, color: '#d1d5db' }}>From:</span>
              <span>{from}</span>
              {to && (
                <>
                  <span style={{ fontWeight: 600, color: '#d1d5db' }}>To:</span>
                  <span>{to}</span>
                </>
              )}
              {date && (
                <>
                  <span style={{ fontWeight: 600, color: '#d1d5db' }}>Date:</span>
                  <span>{date}</span>
                </>
              )}
            </div>

            <div
              style={{
                fontSize: '13px',
                lineHeight: 1.6,
                color: '#e5e7eb',
                whiteSpace: 'pre-wrap',
                marginTop: '4px',
              }}
            >
              {body}
            </div>
          </div>
        );
      }
    } catch (e) {
      // not JSON
    }
  }

  // 2. Format standard Markdown lines (headings, bold, lists) with real line breaks
  const lines = cleanText.split('\n');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '14px', lineHeight: 1.6 }}>
      {lines.map((line, idx) => {
        const trimmedLine = line.trim();

        // Empty line -> spacing
        if (!trimmedLine) {
          return <div key={idx} style={{ height: '8px' }} />;
        }

        // Horizontal rule
        if (trimmedLine === '---' || trimmedLine === '***') {
          return (
            <hr
              key={idx}
              style={{
                border: 'none',
                borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                margin: '8px 0',
              }}
            />
          );
        }

        // Heading 3 or 2
        if (trimmedLine.startsWith('### ') || trimmedLine.startsWith('## ')) {
          const headingText = trimmedLine.replace(/^#+\s*/, '');
          return (
            <h3
              key={idx}
              style={{
                fontSize: '16px',
                fontWeight: 700,
                color: '#f3f4f6',
                marginTop: idx > 0 ? '6px' : '0',
                marginBottom: '2px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              {renderInlineFormatting(headingText)}
            </h3>
          );
        }

        // Bullet list item
        if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ') || /^\d+\.\s/.test(trimmedLine)) {
          const isOrdered = /^\d+\.\s/.test(trimmedLine);
          const bulletPrefix = isOrdered ? trimmedLine.match(/^\d+\.\s/)[0] : '• ';
          const itemText = trimmedLine.replace(/^(-|\*|\d+\.)\s*/, '');

          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                gap: '8px',
                alignItems: 'flex-start',
                paddingLeft: '4px',
              }}
            >
              <span style={{ color: '#a855f7', fontWeight: 700, flexShrink: 0, minWidth: '14px' }}>
                {bulletPrefix}
              </span>
              <span style={{ color: '#e5e7eb', flex: 1 }}>{renderInlineFormatting(itemText)}</span>
            </div>
          );
        }

        // Regular paragraph line with preserved spacing
        return (
          <div key={idx} style={{ color: '#e5e7eb' }}>
            {renderInlineFormatting(line)}
          </div>
        );
      })}
    </div>
  );
}

export default function ChatArea({
  messages,
  isLoading,
  messagesEndRef
}) {
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [expandedAgentOutputs, setExpandedAgentOutputs] = useState({});

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const toggleAgentDrawer = (msgIdx) => {
    setExpandedAgentOutputs((prev) => ({
      ...prev,
      [msgIdx]: !prev[msgIdx],
    }));
  };

  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px 20px',
        maxWidth: '860px',
        width: '100%',
        margin: '0 auto',
      }}
    >
      {/* Empty State / Clean Welcome Canvas (No clickable suggestion cards) */}
      {messages.length === 0 ? (
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            textAlign: 'center',
            padding: '40px 0',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <Sparkles size={36} className="animate-pulse-subtle" color="#a855f7" />
            <h1
              className="gradient-text"
              style={{
                fontSize: '42px',
                fontWeight: 700,
                letterSpacing: '-0.03em',
                lineHeight: 1.1,
              }}
            >
              Hello, Avik
            </h1>
          </div>
          <p style={{ fontSize: '22px', fontWeight: 500, color: '#9ca3af', letterSpacing: '-0.02em', maxWidth: '480px' }}>
            How can I help you today?
          </p>
        </div>
      ) : (
        /* Messages Thread */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                gap: '14px',
                alignItems: 'flex-start',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
              }}
            >
              {/* Avatar */}
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  background:
                    msg.role === 'user'
                      ? 'rgba(255, 255, 255, 0.1)'
                      : 'linear-gradient(135deg, #a855f7 0%, #3b82f6 50%, #ec4899 100%)',
                  boxShadow: msg.role === 'assistant' ? '0 4px 12px rgba(168, 85, 247, 0.3)' : 'none',
                }}
              >
                {msg.role === 'user' ? <User size={16} color="#d1d5db" /> : <Sparkles size={16} color="#ffffff" />}
              </div>

              {/* Message Content Bubble */}
              <div
                style={{
                  maxWidth: '82%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                }}
              >
                {/* Active Agents Badge Pills (for assistant responses) */}
                {msg.role === 'assistant' && msg.active_agents && msg.active_agents.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                    <span style={{ fontSize: '11px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Layers size={11} color="#a855f7" /> Activated:
                    </span>
                    {msg.active_agents.map((ag) => (
                      <span
                        key={ag}
                        style={{
                          fontSize: '11px',
                          fontWeight: 600,
                          padding: '2px 8px',
                          borderRadius: '12px',
                          background: ag === 'google' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(168, 85, 247, 0.15)',
                          color: ag === 'google' ? '#34d399' : '#c084fc',
                          border: ag === 'google' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(168, 85, 247, 0.3)',
                        }}
                      >
                        {ag === 'google' ? 'GoogleAgent (MCP)' : ag.charAt(0).toUpperCase() + ag.slice(1) + 'Agent'}
                      </span>
                    ))}
                  </div>
                )}

                <div
                  className="prose"
                  style={{
                    padding: msg.role === 'user' ? '12px 18px' : '16px 20px',
                    borderRadius: '18px',
                    background: msg.role === 'user' ? '#1f1f26' : 'rgba(255, 255, 255, 0.03)',
                    border: msg.role === 'user' ? '1px solid rgba(255, 255, 255, 0.08)' : '1px solid rgba(255, 255, 255, 0.05)',
                    color: '#f3f4f6',
                  }}
                >
                  <FormattedMessage content={msg.content} />
                </div>

                {/* Sub-agent outputs inspector (Collapsible Drawer) */}
                {msg.role === 'assistant' && msg.agent_outputs && Object.keys(msg.agent_outputs).length > 0 && (
                  <div style={{ marginTop: '2px' }}>
                    <button
                      onClick={() => toggleAgentDrawer(index)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'none',
                        border: 'none',
                        color: '#9ca3af',
                        fontSize: '11px',
                        cursor: 'pointer',
                        padding: '4px 8px',
                        borderRadius: '6px',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = '#e5e7eb')}
                      onMouseLeave={(e) => (e.currentTarget.style.color = '#9ca3af')}
                    >
                      {expandedAgentOutputs[index] ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                      <span>Orchestration Details ({Object.keys(msg.agent_outputs).length} specialists)</span>
                    </button>

                    {expandedAgentOutputs[index] && (
                      <div
                        style={{
                          marginTop: '6px',
                          padding: '12px',
                          borderRadius: '12px',
                          background: 'rgba(0, 0, 0, 0.3)',
                          border: '1px solid rgba(255, 255, 255, 0.06)',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '8px',
                        }}
                      >
                        {Object.entries(msg.agent_outputs).map(([agentName, rawOutput]) => (
                          <div key={agentName} style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                            <span style={{ fontSize: '11px', fontWeight: 600, color: '#c084fc' }}>
                              [{agentName}]
                            </span>
                            <pre
                              style={{
                                fontSize: '11px',
                                background: '#121216',
                                padding: '8px',
                                borderRadius: '8px',
                                overflowX: 'auto',
                                color: '#d1d5db',
                                maxHeight: '180px',
                                whiteSpace: 'pre-wrap',
                              }}
                            >
                              {rawOutput}
                            </pre>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Copy Action Button */}
                {msg.role === 'assistant' && (
                  <div style={{ display: 'flex', gap: '8px', marginTop: '2px' }}>
                    <button
                      onClick={() => handleCopy(msg.content, index)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: copiedIndex === index ? '#10b981' : '#6b7280',
                        fontSize: '11px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                      }}
                      title="Copy response"
                    >
                      {copiedIndex === index ? <Check size={12} /> : <Copy size={12} />}
                      <span>{copiedIndex === index ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Real-time High-Tech Multi-Agent Activity Animation */}
          {isLoading && (
            <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'linear-gradient(135deg, #a855f7 0%, #3b82f6 50%, #ec4899 100%)',
                  boxShadow: '0 4px 14px rgba(168, 85, 247, 0.4)',
                  flexShrink: 0,
                  marginTop: '4px',
                }}
              >
                <Sparkles size={16} color="#ffffff" className="animate-spin-smooth" />
              </div>

              <RealtimeAgentActivity />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
}
