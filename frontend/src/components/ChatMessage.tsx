/**
 * ChatMessage component
 * Displays individual chat messages with user/assistant styling
 */
import React from 'react';
import type { ChatMessage as ChatMessageType } from '../types';
import './ChatMessage.css';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-header">
          <span className="message-role">
            {isUser ? 'คุณ' : 'SiriForm'}
          </span>
          <span className="message-time">
            {new Date(message.timestamp).toLocaleTimeString('th-TH', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
        </div>
        <div className="message-text">
          {message.content}
        </div>
        {message.confidence !== undefined && (
          <div className="message-confidence">
            <span className="confidence-label">ความมั่นใจ:</span>
            <div className="confidence-bar">
              <div 
                className="confidence-fill"
                style={{ width: `${message.confidence * 100}%` }}
              />
            </div>
            <span className="confidence-value">
              {Math.round(message.confidence * 100)}%
            </span>
          </div>
        )}
        {message.highlighted_fields && message.highlighted_fields.length > 0 && (
          <div className="message-highlights">
            <span className="highlights-label">ฟิลด์ที่อัปเดต:</span>
            <div className="highlights-tags">
              {message.highlighted_fields.map((field, index) => (
                <span key={index} className="highlight-tag">
                  {field}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
