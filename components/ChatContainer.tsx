import React, { useEffect, useRef, useState } from 'react';
import { Message } from '../types';
import ChatMessage from './ChatMessage';
import MessageInput from './MessageInput';
import { sendMessage } from '../services/apiService';

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        '👋 Hello! I am your Disease Predictor assistant.\n\nDescribe your symptoms and I will suggest *possible* conditions. I support English, Hindi (हिंदी), and Odia (ଓଡ଼ିଆ).\n\n⚠️ I do NOT provide prescriptions or replace a doctor — always consult a healthcare professional.',
      timestamp: new Date(),
    },
  ]);
  const [loading, setLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: text, timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const reply = await sendMessage(text, history);
      const botMsg: Message = { id: (Date.now() + 1).toString(), role: 'assistant', content: reply, timestamp: new Date() };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ Error: ${err.message || 'Failed to get response'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto bg-slate-50">
      <div ref={listRef} className="flex-1 overflow-y-auto p-4">
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}
        {loading && <div className="text-sm text-slate-500 italic px-2">Bot is typing…</div>}
      </div>
      <MessageInput onSend={handleSend} disabled={loading} />
      <div className="text-[11px] text-center text-slate-400 py-2 px-4">
        For informational purposes only. Not a substitute for professional medical advice.
      </div>
    </div>
  );
};

export default ChatContainer;
