import React, { useState, useRef, useEffect } from 'react';
import { Send, Image as ImageIcon, Mic, MessageCircle, Bot, User } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export default function Chat() {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'bot', text: '👋 Welcome to AgriChat AI 🌿\n\nI can help you with:\n🌿 Crop disease diagnosis\n📸 Send a crop photo for instant analysis\n💬 Type any farming question\n\nHow can I help with your crops today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const userText = input.trim();
    const newUserMsg = { id: Date.now(), sender: 'user', text: userText };
    setMessages(prev => [...prev, newUserMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const res = await axios.post(`${API_BASE}/chat`, { message: userText });
      
      setIsTyping(false);
      setMessages(prev => [
        ...prev, 
        { id: Date.now()+1, sender: 'bot', text: res.data.response || "No response received." }
      ]);
    } catch (e) {
      console.error(e);
      setIsTyping(false);
      setMessages(prev => [...prev, { 
        id: Date.now()+1, sender: 'bot', 
        text: '⚠️ Connection error. Make sure the FastAPI backend is running on port 8000.' 
      }]);
    }
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Show user message with image preview
    const imageUrl = URL.createObjectURL(file);
    setMessages(prev => [...prev, { 
      id: Date.now(), sender: 'user', 
      text: `📸 Sent an image: ${file.name}`,
      image: imageUrl
    }]);
    setIsTyping(true);

    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('message', 'Analyze this crop image');

      const res = await axios.post(`${API_BASE}/chat/image`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setIsTyping(false);
      setMessages(prev => [
        ...prev, 
        { id: Date.now()+1, sender: 'bot', text: res.data.response || "Image analysis failed." }
      ]);
    } catch (e) {
      console.error(e);
      setIsTyping(false);
      setMessages(prev => [...prev, { 
        id: Date.now()+1, sender: 'bot', 
        text: '⚠️ Failed to analyze image. Make sure the backend is running.' 
      }]);
    }

    // Reset file input
    e.target.value = '';
  };

  return (
    <div>
      <h2>🤖 Telegram Bot Chat</h2>
      <p className="subtitle">
        Chat directly with the AgriChat AI — same intelligence that powers the Telegram bot
      </p>

      <div className="chat-container">
        <div className="chat-header">
          <span className="title"><MessageCircle size={20} color="var(--primary)"/> AgriChat Telegram Bot</span>
          <span className="status-indicator">
            <span className="status-dot"></span> Server Connected
          </span>
        </div>
        
        <div className="chat-messages">
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.sender === 'bot' ? 'msg-bot' : 'msg-user'}`}>
              {msg.image && (
                <img 
                  src={msg.image} 
                  alt="Uploaded crop" 
                  style={{
                    maxWidth: '200px', 
                    borderRadius: '12px', 
                    marginBottom: '8px', 
                    display: 'block'
                  }} 
                />
              )}
              {msg.text.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i < msg.text.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))}
            </div>
          ))}
          {isTyping && (
            <div className="message msg-bot" style={{display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', width: 'fit-content'}}>
              <span className="status-dot" style={{animationDelay: '0ms'}}></span>
              <span className="status-dot" style={{animationDelay: '150ms'}}></span>
              <span className="status-dot" style={{animationDelay: '300ms'}}></span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-area">
          <input 
            type="file" 
            ref={fileInputRef}
            accept="image/*" 
            style={{display: 'none'}}
            onChange={handleImageUpload}
          />
          <button 
            className="icon-btn" 
            title="Upload Crop Image for Analysis"
            onClick={() => fileInputRef.current?.click()}
          >
            <ImageIcon size={22} />
          </button>
          <input 
            type="text" 
            className="chat-input" 
            placeholder="Ask about crops, diseases, farming tips..." 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button className="send-btn" onClick={sendMessage}>
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
