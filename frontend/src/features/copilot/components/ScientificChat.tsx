import React, { useState, useEffect, useRef } from 'react';
import { apiRequest } from '../../../services/api';
import { Send, FileDown, Database, Compass, FlaskConical, Brain, Sparkles, RefreshCw } from 'lucide-react';

interface Citation {
  citation_id: string;
  source: string;
  content_snippet: string;
  entity_id: string;
}

interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  citations_json?: string;
  created_at?: string;
}

interface ScientificChatProps {
  sessionId: number | null;
  onSessionCreated: (id: number) => void;
  onWidgetGenerated: (type: 'query' | 'dashboard' | 'workflow', data: any) => void;
}

export const ScientificChat: React.FC<ScientificChatProps> = ({ 
  sessionId, 
  onSessionCreated,
  onWidgetGenerated
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [exporting, setExporting] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load message history on session change
  useEffect(() => {
    if (sessionId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  // Scroll to bottom
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadMessages = async () => {
    try {
      const data = await apiRequest(`/copilot/chat/sessions/${sessionId}/messages`, { service: 'ai' });
      setMessages(data);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const queryText = textToSend || input;
    if (!queryText.trim()) return;

    let activeSessionId = sessionId;

    setIsLoading(true);
    if (!textToSend) setInput('');

    try {
      // 1. Create session if none active
      if (!activeSessionId) {
        const session = await apiRequest('/copilot/chat/sessions', {
          service: 'ai',
          method: 'POST',
          body: JSON.stringify({ title: queryText.substring(0, 40) + '...' })
        });
        activeSessionId = session.id;
        onSessionCreated(session.id);
      }

      // Add user message locally
      const localUserMsg: Message = { role: 'user', content: queryText };
      setMessages((prev) => [...prev, localUserMsg]);

      // 2. Fetch answer
      const resMsg = await apiRequest(`/copilot/chat/sessions/${activeSessionId}/respond`, {
        service: 'ai',
        method: 'POST',
        body: JSON.stringify({ message: queryText })
      });

      setMessages((prev) => [...prev, resMsg]);

      // 3. Inspect if response triggers automated layouts/widgets
      detectAndGenerateWidgets(queryText);

    } catch (err) {
      console.error('Failed to chat:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const detectAndGenerateWidgets = async (text: string) => {
    const q = text.toLowerCase();
    try {
      if (q.includes('dashboard') || q.includes('chart') || q.includes('plotly')) {
        const dashboard = await apiRequest('/copilot/dashboard', {
          service: 'ai',
          method: 'POST',
          body: JSON.stringify({ prompt: text })
        });
        onWidgetGenerated('dashboard', dashboard);
      } else if (q.includes('workflow') || q.includes('flow') || q.includes('benchling daily')) {
        const workflow = await apiRequest('/copilot/workflow', {
          service: 'ai',
          method: 'POST',
          body: JSON.stringify({ prompt: text })
        });
        onWidgetGenerated('workflow', workflow);
      } else if (q.includes('query') || q.includes('egfr') || q.includes('assays')) {
        const queryPlan = await apiRequest('/copilot/query-plan', {
          service: 'ai',
          method: 'POST',
          body: JSON.stringify({ query: text })
        });
        onWidgetGenerated('query', queryPlan);
      }
    } catch (err) {
      console.error('Widget generation failed:', err);
    }
  };

  const handleExport = async (format: 'excel' | 'pdf' | 'ppt') => {
    if (messages.length === 0) return;
    setExporting(format);
    try {
      // Find the last assistant message and retrieve grounded data
      const assistantMsgs = messages.filter(m => m.role === 'assistant');
      const lastMsg = assistantMsgs[assistantMsgs.length - 1];
      const citations: Citation[] = JSON.parse(lastMsg?.citations_json || '[]');

      const payload = {
        title: `AI Scientist Report - Session ${sessionId || 'New'}`,
        format,
        description: lastMsg?.content || 'Scientific Summary',
        data: citations.map(c => ({
          Source: c.source,
          EntityID: c.entity_id,
          Snippet: c.content_snippet
        }))
      };

      const response = await fetch('http://localhost:8010/api/v1/copilot/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `discover_ai_report_${sessionId || 'new'}.${format === 'excel' ? 'xlsx' : format === 'pdf' ? 'pdf' : 'json'}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (err) {
      console.error('Failed to export:', err);
    } finally {
      setExporting(null);
    }
  };

  // Helper to render customized scientific markdown nicely in CSS
  const renderContent = (content: string) => {
    const lines = content.split('\n');
    return lines.map((line, idx) => {
      // Headers
      if (line.startsWith('### ')) {
        return <h3 key={idx} className="text-sm font-bold text-white mt-4 mb-2">{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('#### ')) {
        return <h4 key={idx} className="text-xs font-semibold text-slate-200 mt-3 mb-1">{line.replace('#### ', '')}</h4>;
      }
      // Bullet items
      if (line.trim().startsWith('- ')) {
        const formatted = parseBoldAndCitations(line.trim().substring(2));
        return <li key={idx} className="ml-4 list-disc text-xs text-slate-300 py-0.5">{formatted}</li>;
      }
      // Regular text line
      if (line.trim() === '') return <div key={idx} className="h-2" />;
      return <p key={idx} className="text-xs text-slate-300 leading-relaxed mb-1.5">{parseBoldAndCitations(line)}</p>;
    });
  };

  const parseBoldAndCitations = (text: string) => {
    // Basic regex parser for bold text **word**, citations [1], and markdown images
    const parts = text.split(/(\*\*.*?\*\*|\[\d+\]|!\[.*?\]\(.*?\))/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
      }
      if (part.match(/^\[\d+\]$/)) {
        return <span key={i} className="bg-sky-500/20 text-sky-400 border border-sky-500/30 px-1 py-0.5 rounded text-[10px] font-mono mx-0.5 select-none">{part}</span>;
      }
      if (part.startsWith('![') && part.endsWith(')')) {
        const altMatch = part.match(/!\[(.*?)\]/);
        const urlMatch = part.match(/\((.*?)\)/);
        const alt = altMatch ? altMatch[1] : '';
        const url = urlMatch ? urlMatch[1] : '';
        return (
          <div key={i} className="my-2 p-2 bg-[#090d16] border border-[#1b263b] rounded-lg block">
            <img src={url} alt={alt} className="max-w-[240px] h-auto rounded block mx-auto bg-white p-1" />
            {alt && <div className="text-[9px] text-slate-400 mt-1.5 text-center font-bold uppercase tracking-wider">{alt}</div>}
          </div>
        );
      }
      return part;
    });
  };

  return (
    <div className="flex flex-col h-full bg-[#0a0f1d] rounded-xl border border-[#1e293b] overflow-hidden shadow-2xl">
      {/* Header */}
      <div className="p-4 bg-[#0e1628] border-b border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Brain className="h-5 w-5 text-sky-400" />
          <div>
            <h2 className="text-sm font-bold text-white flex items-center">
              Scientific Chat assistant
              <Sparkles className="h-3 w-3 text-amber-400 ml-1.5 animate-pulse" />
            </h2>
            <p className="text-[10px] text-slate-400">RAG Grounded in ELN, LIMS, & Sequences</p>
          </div>
        </div>

        {/* Exports */}
        {messages.length > 0 && (
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleExport('pdf')}
              disabled={!!exporting}
              className="px-2.5 py-1 rounded bg-[#131d35] hover:bg-[#1b2a4c] text-slate-300 text-xs border border-[#2e3e5c] transition-all flex items-center space-x-1"
            >
              <FileDown className="h-3 w-3" />
              <span>PDF</span>
            </button>
            <button
              onClick={() => handleExport('excel')}
              disabled={!!exporting}
              className="px-2.5 py-1 rounded bg-[#131d35] hover:bg-[#1b2a4c] text-slate-300 text-xs border border-[#2e3e5c] transition-all flex items-center space-x-1"
            >
              <FileDown className="h-3 w-3" />
              <span>Excel</span>
            </button>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 max-w-sm mx-auto">
            <Brain className="h-10 w-10 text-sky-500/40" />
            <h3 className="text-sm font-semibold text-white">AnalytiX AI Copilot</h3>
            <p className="text-xs text-slate-400">
              Ask chemical structures, target activity (EGFR), assay throughputs, sequence alignment interpretations, or automate scientific workflows.
            </p>
            <div className="grid grid-cols-1 gap-2 w-full pt-4">
              <button
                onClick={() => handleSend("Show compounds active against EGFR with IC50 < 100 nM")}
                className="text-left text-xs bg-[#131d35] hover:bg-[#1c2b4e] p-2.5 rounded-lg border border-[#223356] text-slate-300 transition-all flex items-center space-x-2"
              >
                <FlaskConical className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>"Show compounds active against EGFR with IC50 &lt; 100 nM"</span>
              </button>
              <button
                onClick={() => handleSend("Find assays executed last month")}
                className="text-left text-xs bg-[#131d35] hover:bg-[#1c2b4e] p-2.5 rounded-lg border border-[#223356] text-slate-300 transition-all flex items-center space-x-2"
              >
                <Database className="h-4 w-4 text-blue-400 shrink-0" />
                <span>"Find assays executed last month"</span>
              </button>
              <button
                onClick={() => handleSend("Create a workflow that syncs Benchling daily, runs sequence alignment, and emails results.")}
                className="text-left text-xs bg-[#131d35] hover:bg-[#1c2b4e] p-2.5 rounded-lg border border-[#223356] text-slate-300 transition-all flex items-center space-x-2"
              >
                <Compass className="h-4 w-4 text-purple-400 shrink-0" />
                <span>"Create a workflow that syncs Benchling daily..."</span>
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isAssistant = msg.role === 'assistant';
            const citations: Citation[] = isAssistant ? JSON.parse(msg.citations_json || '[]') : [];

            return (
              <div key={index} className={`flex flex-col ${isAssistant ? 'items-start' : 'items-end'} space-y-1`}>
                <span className="text-[9px] text-slate-500 font-semibold px-1">
                  {isAssistant ? 'Discover AI' : 'You'}
                </span>
                <div
                  className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed border ${
                    isAssistant
                      ? 'bg-[#10172a] text-slate-200 border-[#1e293b]'
                      : 'bg-sky-600 text-white border-sky-500 shadow-[0_0_15px_rgba(14,165,233,0.15)]'
                  }`}
                >
                  {isAssistant ? renderContent(msg.content) : msg.content}
                </div>

                {/* Render Citations */}
                {isAssistant && citations.length > 0 && (
                  <div className="w-[85%] mt-2 pl-2 border-l border-sky-500/40 space-y-1">
                    <p className="text-[9px] text-sky-400 font-bold uppercase tracking-wider mb-1">Retrieval Citations</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                      {citations.map((c, cIdx) => (
                        <div
                          key={cIdx}
                          className="bg-[#0b101c] p-2 rounded border border-[#223354] flex flex-col space-y-0.5 text-[10px]"
                        >
                          <div className="flex justify-between items-center text-slate-400 font-semibold">
                            <span className="text-sky-400">{c.citation_id} {c.source}</span>
                            <code className="text-[9px] text-amber-300 font-mono">{c.entity_id}</code>
                          </div>
                          <span className="text-slate-400 truncate text-[9px] mt-0.5">"{c.content_snippet}"</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}

        {isLoading && (
          <div className="flex flex-col items-start space-y-1">
            <span className="text-[9px] text-slate-500 font-semibold px-1">Discover AI</span>
            <div className="bg-[#10172a] rounded-2xl p-3 border border-[#1e293b] flex items-center space-x-2">
              <RefreshCw className="h-3.5 w-3.5 text-sky-400 animate-spin" />
              <span className="text-xs text-slate-400">Grounding response against data catalog...</span>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="p-3 bg-[#0d1324] border-t border-[#1e293b] flex items-center space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a scientific question..."
          className="flex-1 bg-[#151d30] border border-[#253554] rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-all"
        />
        <button
          onClick={() => handleSend()}
          disabled={isLoading || !input.trim()}
          className="p-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white disabled:bg-slate-800 disabled:text-slate-600 transition-all"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
