"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [authState, setAuthState] = useState({
    token: null,
    user: null,
    isCheckingAuth: true,
  });

  const router = useRouter();

  useEffect(() => {
    const stored = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    
    setAuthState({
      token: stored || null,
      user: storedUser ? JSON.parse(storedUser) : null,
      isCheckingAuth: false,
    });
  }, []);

  const login = (accessToken, userInfo) => {
    localStorage.setItem("token", accessToken);
    localStorage.setItem("user", JSON.stringify(userInfo));
    setAuthState({
      token: accessToken,
      user: userInfo,
      isCheckingAuth: false,
    });
    router.push("/chat");
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setAuthState({
      token: null,
      user: null,
      isCheckingAuth: false,
    });
    router.push("/login");
  };

  return (
    <AuthContext.Provider 
      value={{ 
        token: authState.token, 
        user: authState.user, 
        login, 
        logout, 
        isAuthenticated: !!authState.token, 
        isCheckingAuth: authState.isCheckingAuth 
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
