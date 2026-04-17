"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Sidebar from "@/components/sidebar/Sidebar";
import ChatArea from "@/components/chat/ChatArea";
import { getProfile } from "@/services/api";

export default function ChatPage() {
  const { user, logout, isAuthenticated, isCheckingAuth } = useAuth();
  const router = useRouter();
  
  const [profile, setProfile] = useState({});
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isCheckingAuth && isAuthenticated === false) {
      router.replace("/login");
    }
  }, [isAuthenticated, isCheckingAuth, router]);

  // Fetch profile on load
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const fetchProfile = async () => {
      try {
        const res = await getProfile();
        setProfile(res.data.profile || {});
      } catch (err) {
        console.error("Failed to load profile", err);
      }
    };
    fetchProfile();
  }, [isAuthenticated]);

  // Start a new chat session (lazy)
  const handleNewChat = () => {
      setSessionId(null);
      setMessages([]); // Clear chat history
  };

  // Initially create a session if none exists
  // (Removed: We now generate the session lazily on the first message in ChatArea)

  if (isCheckingAuth) return null; // Avoid flicker while checking auth
  if (!isAuthenticated) return null; // Avoid flicker before redirect

  return (
    <div className="flex h-screen bg-kp-purple-pale font-sans">
      <Sidebar 
        profile={profile} 
        onNewChat={handleNewChat} 
        onLogout={logout} 
        userEmail={user?.email} 
      />
      
      {/* Main Content Area (offset by sidebar width) */}
      <main className="ml-72 flex-1 h-full shadow-[-10px_0_30px_rgba(0,0,0,0.05)] relative z-10">
        <ChatArea 
          sessionId={sessionId} 
          setSessionId={setSessionId}
          messages={messages} 
          setMessages={setMessages} 
          setProfile={setProfile}
        />
      </main>
    </div>
  );
}
