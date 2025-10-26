
import React from 'react';
import type { Message } from '../types';
import { BotIcon, UserIcon, SourceIcon } from './Icons';

interface ChatMessageProps {
  message: Message;
  isStreaming: boolean;
}

const ThinkingIndicator: React.FC = () => (
  <div className="flex items-center space-x-1">
    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-dot-pulse-1"></div>
    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-dot-pulse-2"></div>
    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-dot-pulse-3"></div>
  </div>
);

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, isStreaming }) => {
  const isUser = message.role === 'user';
  const isLoading = isStreaming && message.role === 'model' && message.content === '';

  const formattedContent = message.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  return (
    <div className={`flex items-start gap-3 w-full ${isUser ? 'justify-end' : ''}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-muted flex-shrink-0 flex items-center justify-center">
          <BotIcon className="w-5 h-5 text-muted-foreground" />
        </div>
      )}
      <div
        className={`flex flex-col max-w-[80%] ${
          isUser ? 'items-end' : 'items-start'
        }`}
      >
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-primary text-primary-foreground rounded-br-none'
              : 'bg-muted rounded-bl-none'
          }`}
        >
          {isLoading ? (
            <ThinkingIndicator />
          ) : (
            <p className="whitespace-pre-wrap leading-relaxed" dangerouslySetInnerHTML={{ __html: formattedContent }}></p>
          )}
        </div>
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-2 mb-2 font-semibold">
              <SourceIcon className="w-4 h-4" />
              <span>Sources</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {message.sources.map((source, index) => (
                <a
                  key={index}
                  href={source.uri}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-background hover:bg-muted/50 p-2 rounded-md truncate transition-colors"
                >
                  <p className="font-medium truncate">{source.title}</p>
                  <p className="text-muted-foreground/70 truncate">{source.uri}</p>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-muted flex-shrink-0 flex items-center justify-center">
          <UserIcon className="w-5 h-5 text-muted-foreground" />
        </div>
      )}
    </div>
  );
};
