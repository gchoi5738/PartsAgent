import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

axios.defaults.withCredentials = true;
axios.defaults.headers.common['Content-Type'] = 'application/json';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    
    const thinkingId = Date.now(); // Used to identify this thinking message
    setMessages(prev => [...prev, {
      id: thinkingId,
      role: 'thinking',
      content: 'Thinking...'
    }]);
    
    setIsLoading(true);
    setInput('');

    try {
      const response = await axios.post('http://localhost:8000/api/chat/', {
        message: input
      });

      // Remove thinking message and add response
      setMessages(prev => prev
        .filter(msg => msg.id !== thinkingId) // Remove thinking message
        .concat({
          role: 'assistant',
          content: response.data.response
        })
      );
    } catch (error) {
      // Remove thinking message and add error
      setMessages(prev => prev
        .filter(msg => msg.id !== thinkingId)
        .concat({
          role: 'error',
          content: 'Sorry, there was an error processing your request.'
        })
      );
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message) => {
    const isUser = message.role === 'user';
    const isThinking = message.role === 'thinking';

    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div 
          className={`
            rounded-lg px-6 py-4 max-w-[80%] shadow-sm
            ${isUser ? 'bg-blue-500 text-white ml-4' : ''}
            ${isThinking ? 'bg-gray-100 text-gray-600 italic' : ''}
            ${(!isUser && !isThinking) ? 'bg-white border border-gray-200' : ''}
          `}
        >
          {!isUser && !isThinking && (
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mb-2">
              <span className="text-blue-500 text-sm font-semibold">PS</span>
            </div>
          )}
          {isThinking && (
            <div className="text-xs font-semibold text-gray-500 mb-1">Thinking...</div>
          )}
          <div className="prose">
            <p className="whitespace-pre-wrap text-sm md:text-base m-0">
              {message.content}
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Main chat container */}
      <div className="max-w-3xl mx-auto h-screen flex flex-col">
        {/* Header */}
        <div className="py-6 px-4 text-center">
          <h1 className="text-2xl font-bold text-gray-800">PartSelect Assistant</h1>
          <p className="text-sm text-gray-500 mt-1">
            Helping you find the right parts for your appliances
          </p>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-4">
          <div className="space-y-4 py-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <p className="text-sm">
                  Ask me about refrigerator and dishwasher parts, installations, or troubleshooting.
                </p>
              </div>
            )}
            {messages.map((message, index) => (
              <div key={index}>{renderMessage(message)}</div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg px-6 py-4">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Form */}
        <div className="border-t bg-white p-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-4 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm bg-gray-50"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 rounded-xl bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 text-sm font-medium transition-colors"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}