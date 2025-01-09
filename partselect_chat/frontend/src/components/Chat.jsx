import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

const Spinner = () => (
  <div 
    style={{
      display: 'inline-block',
      width: '24px',
      height: '24px',
      border: '4px solid rgba(0, 0, 0, 0.1)',
      borderTop: '4px solid #2563eb', // Blue color for the spinning part
      borderRadius: '50%',
      animation: 'spin 1s linear infinite',
    }}
  />
);

const Chat = ({ currentUrl }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleLinkClick = (e) => {
    const href = e.target.getAttribute('href');
    if (href && (href.startsWith('/parts/') || href.startsWith('/installation-guides/'))) {
      e.preventDefault();
      navigate(href);
    }
  };

  const sendMessage = async () => {
    if (inputValue.trim() === '') return;

    setMessages(prev => [...prev, { sender: 'user', content: inputValue }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: inputValue,
          currentUrl: currentUrl
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        content: data.response,
        context: data.context
      }]);

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        content: 'An error occurred. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-blue-600 text-white p-4 shadow-md">
        <h1 className="text-xl font-semibold">PartSelect Support Chat</h1>
        <p className="text-sm text-blue-100">Ask me about parts, installation guides, or policies</p>
      </div>

      <div className="flex-grow overflow-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`p-2 rounded-lg ${
              msg.sender === 'user' 
                ? 'bg-blue-100 ml-auto' 
                : 'bg-gray-100'
            } max-w-[80%]`}
          >
            <div className="font-semibold mb-1">
              {msg.sender === 'user' ? 'You:' : 'Assistant:'}
            </div>
            <div 
              onClick={handleLinkClick} 
              className="prose max-w-none"
            >
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-center p-4">
            <Spinner />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            className="flex-grow p-2 border rounded"
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            disabled={isLoading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;