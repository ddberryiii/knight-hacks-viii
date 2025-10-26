
import React, { useState, useEffect, useRef } from 'react';
import type { Message } from './types';
import { streamChatResponse, extractSources } from './services/geminiService';
import { ChatInput } from './components/ChatInput';
import { ChatMessage } from './components/ChatMessage';
import { BotIcon } from './components/Icons';

const App: React.FC = () => {
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Show a welcome message on first load
    setChatHistory([
        {
            id: 'welcome-message',
            role: 'model',
            content: "Hello! I'm Gemini, your AI assistant. I can answer your questions with up-to-date information from Google Search. How can I help you today?"
        }
    ]);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isLoading]);

  const handleSendMessage = async (userInput: string) => {
    setIsLoading(true);
    setError(null);

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userInput,
    };
    
    const modelMessagePlaceholder: Message = {
        id: `model-${Date.now()}`,
        role: 'model',
        content: '',
    };

    setChatHistory((prev) => [...prev, userMessage, modelMessagePlaceholder]);

    try {
      const stream = await streamChatResponse(userInput);
      let fullResponseText = '';
      
      for await (const chunk of stream) {
        fullResponseText += chunk.text;
        setChatHistory((prev) => {
            const newHistory = [...prev];
            const lastMessage = newHistory[newHistory.length - 1];
            if (lastMessage && lastMessage.role === 'model') {
                lastMessage.content = fullResponseText;
            }
            return newHistory;
        });
      }

      // After stream is complete, get the final response object to extract sources
      const finalResponse = await stream.response;
      const sources = extractSources(finalResponse);

      setChatHistory((prev) => {
        const newHistory = [...prev];
        const lastMessage = newHistory[newHistory.length - 1];
        if (lastMessage && lastMessage.role === 'model') {
            lastMessage.sources = sources;
        }
        return newHistory;
      });

    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred.';
      setError(`Error: ${errorMessage}`);
      setChatHistory((prev) => {
        const newHistory = [...prev];
        const lastMessage = newHistory[newHistory.length - 1];
        if (lastMessage && lastMessage.role === 'model') {
            lastMessage.content = `Sorry, I ran into an issue. ${errorMessage}`;
        }
        return newHistory;
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col items-center bg-background p-4">
      <div className="flex flex-col w-full max-w-3xl h-full bg-background">
        <header className="p-4 border-b border-muted flex items-center gap-3">
            <BotIcon className="w-8 h-8 text-primary"/>
            <div>
                <h1 className="text-xl font-bold text-foreground">Gemini Insight Chat</h1>
                <p className="text-sm text-muted-foreground">Powered by gemini-2.5-flash & Google Search</p>
            </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 space-y-6">
          {chatHistory.map((msg, index) => (
            <ChatMessage 
                key={msg.id} 
                message={msg} 
                isStreaming={isLoading && index === chatHistory.length - 1}
            />
          ))}
          <div ref={chatEndRef} />
        </main>

        <footer className="p-4">
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
          {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}
        </footer>
      </div>
    </div>
  );
};

export default App;
