import { Gift } from "lucide-react";

const SUGGESTIONS = [
  "I need a birthday gift for my mom who loves flowers",
  "What are some good chocolate gifts under Rs. 5000?",
  "Show me gifts for a newborn baby. I want to deliver it to Panadura.",
  "Can you suggest an anniversary gift for my husband?"
];

export default function WelcomeMessage() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4 animate-in fade-in duration-500">
      <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-lg border border-kp-gold/20 mb-6">
        <Gift className="w-10 h-10 text-kp-gold" />
      </div>
      <h1 className="text-3xl font-bold text-kp-purple-deep mb-3">
        How can I help you find the perfect gift?
      </h1>
      <p className="text-gray-500 max-w-2xl mx-auto mb-8 text-lg">
        I am your AI-powered Kapruka Gift Concierge. Tell me about the person you&apos;re shopping for, the occasion, delivery location or your budget.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl text-left">
        {SUGGESTIONS.map((suggestion, i) => (
          <div 
            key={i}
            className="p-4 bg-white border border-gray-100 rounded-xl hover:border-kp-gold hover:shadow-md cursor-pointer transition-all text-sm text-gray-700"
          >
            &quot;{suggestion}&quot;
          </div>
        ))}
      </div>
    </div>
  );
}
