import React from 'react';
import ChatContainer from './components/ChatContainer';

const App: React.FC = () => {
  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white text-lg">🩺</div>
          <div>
            <h1 className="font-semibold text-slate-800 leading-none">Disease Predictor Chatbot</h1>
            <p className="text-xs text-slate-500">Multilingual • English • हिंदी • ଓଡ଼ିଆ • via Gemini</p>
          </div>
        </div>
        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          className="text-xs bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-full text-slate-700"
        >
          API Docs
        </a>
      </header>
      <main className="flex-1 overflow-hidden">
        <ChatContainer />
      </main>
    </div>
  );
};

export default App;
