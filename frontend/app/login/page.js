"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { signIn, signUp } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Gift, ShoppingBag, Sparkles } from "lucide-react";

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isLogin) {
        const response = await signIn(email, password);
        login(response.data.access_token, { email });
      } else {
        await signUp(email, password);
        // Auto sign-in after signup
        const response = await signIn(email, password);
        login(response.data.access_token, { email });
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Panel */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-kp-purple-deep to-kp-purple-main flex-col items-center justify-center p-12 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/10 via-transparent to-transparent opacity-50" />
        
        <h2 className="text-5xl font-extrabold flex items-center gap-4 mb-12 tracking-wide z-10 group cursor-default">
          <div className="p-3 bg-gradient-to-br from-kp-gold to-kp-gold-dark rounded-2xl shadow-[0_0_25px_rgba(245,166,35,0.4)]">
            <ShoppingBag className="text-kp-purple-deep w-10 h-10 stroke-[2.5]" />
          </div>
          <span className="bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent drop-shadow-sm ml-1">
            KAPRUKA
          </span>
        </h2>
        
        <div className="relative w-64 h-64 mb-12 z-10 bg-white/10 rounded-2xl p-8 backdrop-blur-sm border border-white/20 shadow-2xl flex items-center justify-center">
          <Gift className="w-32 h-32 text-kp-gold-dark" />
        </div>
        
        <h1 className="text-4xl font-semibold mb-4 z-10 text-center text-balance">
          Your AI-Powered Gift Concierge
        </h1>
        <p className="text-kp-purple-pale/80 text-center max-w-md z-10">
          Find the perfect gift for any occasion, tailored to your loved ones&apos; preferences.
        </p>
      </div>

      {/* Right Panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-gray-50 p-8">
        <Card className="w-full max-w-md shadow-lg border-white">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-kp-purple-deep">
              {isLogin ? "Sign In" : "Create an Account"}
            </CardTitle>
            <CardDescription>
              {isLogin
                ? "Enter your email and password to access your concierge."
                : "Enter your email below to create your account."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-700">Email</label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="focus-visible:ring-kp-purple-main"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-gray-700">Password</label>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="focus-visible:ring-kp-purple-main"
                />
              </div>
              
              {error && <p className="text-sm text-kp-danger">{error}</p>}
              
              <Button 
                type="submit" 
                className="w-full bg-kp-purple-deep hover:bg-kp-purple-main text-white" 
                disabled={loading}
              >
                {loading ? "Please wait..." : (isLogin ? "Sign In" : "Sign Up")}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-muted-foreground" />
              </div>
            </div>
            
            <div className="text-center text-sm text-gray-600">
              {isLogin ? "Don&apos;t have an account? " : "Already have an account? "}
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="font-semibold text-kp-purple-deep hover:text-kp-purple-main hover:underline"
              >
                {isLogin ? "Sign Up" : "Sign In"}
              </button>
            </div>
            
            <div className="flex items-center justify-center gap-2 pt-4 text-xs font-medium text-kp-purple-deep/70 bg-kp-purple-pale px-4 py-2 rounded-full mx-auto">
              <Sparkles className="w-3 h-3" />
              Powered by AI
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
