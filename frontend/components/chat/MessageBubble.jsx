import { Avatar } from "@/components/ui/avatar";
import { Gift, ChevronDown, Check } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import { memo } from "react";

const MessageBubble = memo(function MessageBubble({ role, content, statuses = [] }) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-4 w-full ${isUser ? "flex-row-reverse" : "flex-row"} mb-8 animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      {/* Avatar */}
      {!isUser && (
        <Avatar className="h-10 w-10 border border-black/5 bg-white shadow-sm flex-shrink-0 flex items-center justify-center">
          <Gift className="w-5 h-5 text-kp-gold" />
        </Avatar>
      )}

      {/* Bubble */}
      <div className={`flex flex-col gap-3 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        <div 
          className={`px-5 py-3.5 rounded-2xl ${
            isUser 
              ? "bg-kp-purple-deep text-white rounded-tr-sm" 
              : "bg-white text-gray-800 shadow-sm border border-gray-100 rounded-tl-sm"
          }`}
        >
          {/* Custom styled markdown components to handle spacing and links since Tailwind prose isn't installed */}
          <div className="text-[15px] leading-relaxed break-words">
            <ReactMarkdown
              components={{
                p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
                a: ({ node, ...props }) => (
                  <a 
                    className="text-kp-purple-main hover:text-kp-purple-deep underline underline-offset-2 font-medium" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    {...props} 
                  />
                ),
                ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-3 space-y-1" {...props} />,
                ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-3 space-y-1" {...props} />,
                li: ({ node, ...props }) => <li className="" {...props} />,
                h3: ({ node, ...props }) => <h3 className="text-base font-bold mt-5 mb-2 text-gray-900" {...props} />,
                strong: ({ node, ...props }) => <strong className="font-bold text-gray-900" {...props} />
              }}
            >
              {content}
            </ReactMarkdown>
          </div>

          {statuses && statuses.length > 0 && !isUser && (
            <div className="mt-4 pt-3 border-t border-gray-100">
              <details className="group">
                <summary className="text-xs font-semibold text-kp-text-muted hover:text-kp-purple-main flex items-center gap-1 cursor-pointer select-none transition-colors w-fit">
                  <span>View thought process</span>
                  <ChevronDown className="w-3.5 h-3.5 group-open:rotate-180 transition-transform duration-200" />
                </summary>
                <div className="mt-2.5 flex flex-col gap-1.5 pl-1">
                  {statuses.map((status, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-xs font-medium text-gray-400">
                      <Check className="w-3 h-3 text-green-500 opacity-70 shrink-0" strokeWidth={3} />
                      <span>{status}</span>
                    </div>
                  ))}
                </div>
              </details>
            </div>
          )}
        </div>
      </div>
    </div>
  );
});

export default MessageBubble;
