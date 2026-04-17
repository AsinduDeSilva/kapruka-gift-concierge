import { memo } from "react";
import { Button } from "@/components/ui/button";
import { Cake, Flower2, Candy, Shirt, Monitor, BellRing } from "lucide-react";

const CATEGORIES = [
  { name: "Cakes", icon: Cake, href: "https://www.kapruka.com/online/cakes"},
  { name: "Flowers", icon: Flower2, href: "https://www.kapruka.com/online/flowers"},
  { name: "Chocolates", icon: Candy, href: "https://www.kapruka.com/online/chocolates"},
  { name: "Clothing", icon: Shirt, href: "https://www.kapruka.com/online/clothing"},
  { name: "Electronics", icon: Monitor, href: "https://www.kapruka.com/online/electronics"},
  { name: "Jewellery", icon: BellRing, href: "https://www.kapruka.com/online/jewellery"},
];

const CategoryGrid = memo(function CategoryGrid() {
  return (
    <div className="grid grid-cols-3 gap-2">
      {CATEGORIES.map((cat) => {
        const Icon = cat.icon;
        return (
          <Button
            key={cat.name}
            variant="default"
            onClick={() => window.open(cat.href, "_blank")}
            className="h-auto py-3 px-1 flex flex-col items-center justify-center gap-2 bg-kp-purple-card hover:bg-white/15 text-white rounded-xl transition-all hover:cursor-pointer"
          >
            <Icon className="w-6 h-6 text-kp-gold" strokeWidth={1.5} />
            <span className="text-[10px] font-medium leading-none">{cat.name}</span>
          </Button>
        );
      })}
    </div>
  );
});

export default CategoryGrid;
