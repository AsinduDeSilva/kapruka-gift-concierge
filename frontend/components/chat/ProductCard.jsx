import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function ProductCard({ title, price, image, link }) {
  // If no image is provided, use a placeholder
  const imageUrl = image || "https://picsum.photos/400/300";
  const productLink = link || "#";

  return (
    <Card className="w-64 flex-shrink-0 overflow-hidden border-gray-200 hover:shadow-md transition-shadow group bg-white">
      <div className="h-40 overflow-hidden relative bg-gray-50">
        <img 
          src={imageUrl} 
          alt={title} 
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <CardContent className="p-4 flex flex-col gap-2">
        <h3 className="font-semibold text-gray-900 line-clamp-2 leading-tight min-h-[40px] text-sm">
          {title}
        </h3>
        <p className="text-kp-gold-dark font-bold">LKR {price}</p>
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full mt-2 border-kp-purple-main text-kp-purple-main hover:bg-kp-purple-main hover:text-white transition-colors"
          asChild
        >
          <a href={productLink} target="_blank" rel="noopener noreferrer">
            View on Kapruka &rarr;
          </a>
        </Button>
      </CardContent>
    </Card>
  );
}
