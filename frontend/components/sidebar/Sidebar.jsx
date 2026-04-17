import { memo } from "react";
import { Button } from "@/components/ui/button";
import { ShoppingBag, Plus, LogOut } from "lucide-react";
import CategoryGrid from "./CategoryGrid";
import RecipientCard from "./RecipientCard";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const Sidebar = memo(function Sidebar({ profile, onNewChat, onLogout, userEmail }) {
  return (
    <div className="w-72 bg-kp-purple-deep h-screen flex flex-col text-white fixed left-0 top-0">
      <div className="p-4 flex-shrink-0">
        <h2 className="text-2xl font-extrabold flex items-center gap-2 mb-6 tracking-wide group cursor-default">
          <div className="p-2 ml-0.5   bg-gradient-to-br from-kp-gold to-kp-gold-dark rounded-xl shadow-[0_0_15px_rgba(245,166,35,0.35)] transition-shadow duration-300">
            <ShoppingBag className="text-kp-purple-deep w-5 h-5 stroke-[2.5]" />
          </div>
          <span className="bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent drop-shadow-sm ml-0.5">
            KAPRUKA
          </span>
        </h2>

        <Button 
          onClick={onNewChat} 
          className="w-full bg-kp-gold hover:bg-kp-gold-dark text-black font-semibold rounded-xl h-12 flex gap-2 cursor-pointer"
        >
          <Plus size={20} />
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-6 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
        <div>
          <h3 className="text-xs font-bold text-kp-text-muted uppercase tracking-wider mb-3 px-1">
            Browse by Category
          </h3>
          <CategoryGrid />
        </div>

        <div>
          <h3 className="text-xs font-bold text-kp-text-muted uppercase tracking-wider mb-3 px-1">
            Recipient Profiles
          </h3>
          <div className="space-y-2">
            {profile && Object.keys(profile).length > 0 ? (
              Object.entries(profile).map(([name, data]) => (
                <RecipientCard 
                  key={name} 
                  name={name} 
                  preferences={data.preferences} 
                  allergies={data.allergies} 
                />
              ))
            ) : (
              <p className="text-sm text-kp-text-muted px-1">No profiles found.</p>
            )}
          </div>
        </div>
      </div>

      <div className="p-4 flex-shrink-0 border-t border-white/10 mt-auto">
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10 border border-white/20 bg-kp-purple-card">
            <AvatarFallback className="text-black">{userEmail?.[0]?.toUpperCase() || 'U'}</AvatarFallback>
          </Avatar>
          <div className="flex-1 overflow-hidden">
            <p className="text-sm font-medium truncate">{userEmail}</p>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            className="text-white hover:bg-white/10 hover:text-white h-8 w-8 transition-colors cursor-pointer"
            onClick={onLogout}
            title="Logout"
          >
            <LogOut size={16} />
          </Button>
        </div>
      </div>
    </div>
  );
});

export default Sidebar;
