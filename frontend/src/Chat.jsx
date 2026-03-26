import React, { useState, useRef, useEffect } from 'react';
import { Send, Image as ImageIcon, Mic, MessageCircle } from 'lucide-react';
import axios from 'axios';

export default function Chat() {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'bot', text: 'Welcome to AgriChat AI 🌿 How can I help with your crops today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    // Add user message to UI
    const newUserMsg = { id: Date.now(), sender: 'user', text: input };
    setMessages(prev => [...prev, newUserMsg]);
    setInput('');
    setIsTyping(true);

    // Send to FastAPI webhook (simulate WhatsApp)
    try {
      const formData = new FormData();
      formData.append('From', 'whatsapp:+19998887777');
      formData.append('Body', newUserMsg.text);
      formData.append('NumMedia', '0');

      // Post to our local FastAPI webhook
      const res = await axios.post('http://127.0.0.1:8000/webhook/', formData);
      
      // Simulate bot response for UI 
      setTimeout(() => {
        setIsTyping(false);
        setMessages(prev => [
            ...prev, 
            { id: Date.now()+1, sender: 'bot', text: res.data.response || "No response received." }
        ]);
      }, 500);

    } catch (e) {
      console.error(e);
      setIsTyping(false);
      setMessages(prev => [...prev, { id: Date.now()+1, sender: 'bot', text: '⚠️ Connection error to FastAPI. Is it running on port 8000?' }]);
    }
  };

  return (
    <div>
      <h2>Farmer Chat Simulator</h2>
      <p className="subtitle">
        Simulates exactly what farmers experience on WhatsApp
      </p>

      <div className="chat-container">
        <div className="chat-header">
          <span className="title"><MessageCircle size={20} color="var(--primary)"/> WhatsApp Gateway</span>
          <span className="status-indicator">
            <span className="status-dot"></span> Server Connected
          </span>
        </div>
        
        <div className="chat-messages">
          {messages.map(msg => (
            <div key={msg.id} className={`message ${msg.sender === 'bot' ? 'msg-bot' : 'msg-user'}`}>
              {msg.text}
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
          <button className="icon-btn" title="Simulate Image Upload (Mock)"><ImageIcon size={22} /></button>
          <button className="icon-btn" title="Simulate Voice Note (Mock)"><Mic size={22} /></button>
          <input 
            type="text" 
            className="chat-input" 
            placeholder="Type a message to the AI..." 
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
