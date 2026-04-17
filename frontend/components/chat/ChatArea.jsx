"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, Check, Gift } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import MessageBubble from "./MessageBubble";
import WelcomeMessage from "./WelcomeMessage";
import { sendMessageStream, createSession } from "@/services/api";

export default function ChatArea({ sessionId, setSessionId, messages, setMessages, setProfile }) {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatuses, setAgentStatuses] = useState([]);
  const bottomRef = useRef(null);

  // Auto-scroll to bottom on new message or status
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, agentStatuses]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput("");
    
    // Optimistic UI update
    const newMessages = [...messages, { role: "user", content: userMsg }];
    setMessages(newMessages);
    setIsLoading(true);

    let currentSessionId = sessionId;

    try {
      if (!currentSessionId) {
        const res = await createSession();
        currentSessionId = res.data.session_id;
        setSessionId(currentSessionId);
      }

      setAgentStatuses([]);
      let currentLocStatuses = [];
      
      await sendMessageStream(
        currentSessionId,
        userMsg,
        (status) => {
          currentLocStatuses.push(status);
          setAgentStatuses([...currentLocStatuses]);
        },
        (reply, profile) => {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: reply, statuses: currentLocStatuses }
          ]);
          if (profile && setProfile) {
            setProfile(profile);
          }
          setIsLoading(false);
          setAgentStatuses([]);
        },
        (error) => {
          console.error("Failed to send message", error);
          setIsLoading(false);
          setAgentStatuses([]);
        }
      );
    } catch (error) {
      console.error("Failed to start chat stream", error);
      setIsLoading(false);
      setAgentStatuses([]);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-kp-purple-pale relative">
      {/* Header */}
      <header className="h-16 px-6 bg-white/80 backdrop-blur-md border-b border-gray-100 flex items-center justify-between sticky top-0 z-10 shadow-sm transition-all">
        <div className="flex items-center gap-3">
          
          <h1 className="text-xl font-bold text-kp-purple-deep tracking-tight">
            Kapruka <span className="font-medium text-gray-400">Gift Concierge</span>
          </h1>
        </div>
        <div className="flex items-center gap-2 text-xs font-semibold text-kp-purple-main bg-kp-purple-main/10 px-3.5 py-1.5 rounded-full border border-kp-purple-main/20">
          <Sparkles className="w-3.5 h-3.5 animate-pulse" />
          Always Ready
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full px-4 lg:px-12 py-8">
          {messages.length === 0 ? (
            <div className="h-full min-h-[60vh] flex items-center justify-center">
                <WelcomeMessage />
            </div>
          ) : (
            <div className="max-w-4xl mx-auto flex flex-col justify-end min-h-full">
              {messages.map((msg, i) => (
                <MessageBubble 
                  key={i} 
                  role={msg.role} 
                  content={msg.content} 
                  statuses={msg.statuses}
                />
              ))}
              
              {isLoading && (
                <div className="flex gap-4 w-full mb-8 items-start">
                  <div className="h-10 w-10 shrink-0 rounded-full bg-gray-200 border border-gray-300 animate-pulse" />
                  <div className="flex flex-col gap-2 w-full max-w-sm">
                    <div className="bg-white px-5 py-4 w-fit rounded-2xl rounded-tl-sm shadow-sm border border-gray-100 flex items-center gap-1 shrink-0">
                      <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" />
                      <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" style={{ animationDelay: "0.2s" }} />
                      <div className="w-2 h-2 rounded-full bg-gray-300 animate-bounce" style={{ animationDelay: "0.4s" }} />
                    </div>
                    {agentStatuses.length > 0 && (
                      <div className="flex flex-col gap-1.5 ml-2 mt-1">
                        {agentStatuses.map((status, idx) => {
                          const isLast = idx === agentStatuses.length - 1;
                          return (
                            <div 
                              key={idx} 
                              className={`flex items-center gap-2 text-xs font-medium transition-all duration-300 ${
                                isLast ? 'text-kp-purple-main animate-pulse' : 'text-gray-400 opacity-60'
                              }`}
                            >
                              {!isLast ? (
                                <Check className="w-3 h-3 text-green-500 shrink-0" strokeWidth={3} />
                              ) : (
                                <div className="w-3 h-3 flex items-center justify-center shrink-0">
                                  <div className="w-1.5 h-1.5 rounded-full bg-kp-purple-main" />
                                </div>
                              )}
                              <span>{status}</span>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              <div ref={bottomRef} className="h-4" />
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-100">
        <form 
          onSubmit={handleSend} 
          className="max-w-4xl mx-auto relative flex items-center"
        >
          <Input 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message here..."
            className="w-full text-base py-6 pl-6 pr-16 rounded-full border-gray-200 focus-visible:ring-kp-gold focus-visible:border-kp-gold shadow-sm"
            disabled={isLoading}
          />
          <Button 
            type="submit" 
            size="icon"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 rounded-full w-10 h-10 bg-kp-gold hover:bg-kp-gold-dark text-white transition-colors"
          >
            <Send className="w-4 h-4 ml-0.5" />
          </Button>
        </form>
        <p className="text-center text-xs text-gray-400 mt-2">
          AI can make mistakes. Always verify product details on the Kapruka website.
        </p>
      </div>
    </div>
  );
}
