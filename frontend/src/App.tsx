/**
 * Main App component
 * Two-column layout: Chat interface on the left, Form preview on the right
 */
import { useState, useEffect, useRef } from 'react';
import type { ChatMessage, FormData, JSONSchema } from './types';
import { ChatMessage as ChatMessageComponent } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { DynamicFormRenderer } from './components/DynamicFormRenderer';
import { ProgressBar } from './components/ProgressBar';
import { sendChatMessage, getFormSchema, generateSessionId } from './services/api';
import { calculateFormProgress } from './utils/formUtils';
import './App.css';

function App() {
  // State management
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [formData, setFormData] = useState<FormData>({});
  const [formSchema, setFormSchema] = useState<JSONSchema | null>(null);
  const [highlightedFields, setHighlightedFields] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const [error, setError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load form schema on mount
  useEffect(() => {
    loadFormSchema();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadFormSchema = async () => {
    try {
      const response = await getFormSchema('equipment_form');
      setFormSchema(response.schema);
      
      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        role: 'assistant',
        content: 'สวัสดีครับ! ยินดีต้อนรับสู่ระบบขอใช้อุปกรณ์คอมพิวเตอร์ ผมจะช่วยคุณกรอกฟอร์มผ่านการสนทนาครับ 😊\n\nคุณต้องการขออุปกรณ์อะไรบ้างครับ? (เช่น "ขอ laptop 2 เครื่อง สำหรับพรุ่งนี้เช้า")',
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    } catch (err) {
      console.error('Failed to load form schema:', err);
      setError('ไม่สามารถโหลดแบบฟอร์มได้ กรุณาลองใหม่อีกครั้ง');
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      // Send to backend
      const response = await sendChatMessage({
        message: content,
        session_id: sessionId,
        form_data: formData,
      });

      // Update form data
      setFormData(response.form_data);
      setHighlightedFields(response.highlighted_fields);

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        highlighted_fields: response.highlighted_fields,
        confidence: response.confidence,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Clear highlights after 3 seconds
      setTimeout(() => {
        setHighlightedFields([]);
      }, 3000);
    } catch (err: any) {
      console.error('Failed to send message:', err);
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `ขออภัยครับ เกิดข้อผิดพลาด: ${err.message || 'ไม่สามารถส่งข้อความได้'}\n\nกรุณาตรวจสอบว่า Backend Server กำลังทำงานอยู่ที่ http://localhost:8000`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate progress
  const progress = formSchema 
    ? calculateFormProgress(formData, formSchema)
    : { percentage: 0, filledFields: 0, totalFields: 0, requiredFields: 0, filledRequiredFields: 0 };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            🤖 SiriForm Agent
          </h1>
          <p className="app-subtitle">
            ระบบขอใช้อุปกรณ์คอมพิวเตอร์แบบสนทนา
          </p>
        </div>
        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}
      </header>

      {/* Main Content - Two Columns */}
      <div className="app-content">
        {/* Left Column - Chat */}
        <div className="chat-column">
          <div className="chat-messages">
            {messages.map((message) => (
              <ChatMessageComponent key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="loading-indicator">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="loading-text">กำลังประมวลผล...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <ChatInput 
            onSend={handleSendMessage} 
            disabled={isLoading}
          />
        </div>

        {/* Right Column - Form Preview */}
        <div className="form-column">
          <div className="form-header">
            <h2 className="form-title">📋 ตัวอย่างฟอร์ม</h2>
            <ProgressBar 
              percentage={progress.percentage}
              label="ความสมบูรณ์"
            />
            <div className="progress-stats">
              <span className="stat-item">
                📝 กรอกแล้ว: {progress.filledRequiredFields}/{progress.requiredFields} ฟิลด์
              </span>
            </div>
          </div>
          <div className="form-content">
            {formSchema ? (
              <DynamicFormRenderer
                schema={formSchema}
                formData={formData}
                highlightedFields={highlightedFields}
                readOnly={true}
              />
            ) : (
              <div className="loading-form">
                <div className="loading-spinner"></div>
                <p>กำลังโหลดฟอร์ม...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
