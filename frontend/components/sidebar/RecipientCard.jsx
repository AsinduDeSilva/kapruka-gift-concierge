import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { UserCircle } from "lucide-react";

export default function RecipientCard({ name, preferences = [], allergies = [] }) {
  return (
    <Accordion type="single" className="w-full bg-kp-purple-card rounded-xl overflow-hidden border-none">
      <AccordionItem value="item-1" className="border-none">
        <AccordionTrigger className="px-4 py-3 hover:no-underline hover:bg-white/5 transition-colors">
          <div className="flex items-center gap-3 text-left">
            <UserCircle className="w-6 h-6 text-kp-gold" />
            <span className="font-semibold capitalize text-base">{name}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4 pb-4 pt-1 bg-black/10">
          <div className="space-y-3">
            <div>
              <p className="text-xs text-kp-text-muted mb-1.5 font-medium">Preferences</p>
              <div className="flex flex-wrap gap-1.5">
                {preferences.length > 0 ? (
                  preferences.map((p) => (
                    <Badge key={p} variant="secondary" className="bg-white/10 text-white font-normal hover:bg-white/20 border-transparent text-xs">
                      {p}
                    </Badge>
                  ))
                ) : (
                  <span className="text-xs text-white/50">Not specified</span>
                )}
              </div>
            </div>
            
            <div>
              <p className="text-xs text-kp-text-muted mb-1.5 font-medium">Allergies</p>
              <div className="flex flex-wrap gap-1.5">
                {allergies.length > 0 ? (
                  allergies.map((p) => (
                    <Badge key={p} variant="secondary" className="bg-white/10 text-white font-normal hover:bg-white/20 border-transparent text-xs">
                      {p}
                    </Badge>
                  ))
                ) : (
                  <span className="text-xs text-white/50">Not specified</span>
                )}
              </div>
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
