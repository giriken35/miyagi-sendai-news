import React from "react";

export interface NewsItem {
  title: string;
  link: string;
  published: string;
  source_name: string;
  source_key: string;
  source_emoji: string;
  summary: string;
  category?: string;
}

export default function NewsCard({ item }: { item: NewsItem }) {
  const pubDate = new Date(item.published);
  
  // Format MM/DD
  const month = (pubDate.getMonth() + 1).toString().padStart(2, "0");
  const date = pubDate.getDate().toString().padStart(2, "0");
  const dayStr = `${month}/${date}`;

  // Format HH:MM
  const hours = pubDate.getHours().toString().padStart(2, "0");
  const minutes = pubDate.getMinutes().toString().padStart(2, "0");
  const timeStr = `${hours}:${minutes}`;

  // Source Badge Styles
  const getBadgeStyle = (key: string) => {
    switch (key) {
      case "kahoku": return "bg-[#DDE8F5] text-[#1A3A6E]";
      case "tushin": return "bg-[#F5E8DD] text-[#6E3A1A]";
      case "yahoo": return "bg-[#DDF5E8] text-[#1A6E3A]";
      default: return "bg-[#EDE8DC] text-[#5A4A3A]";
    }
  };

  return (
    <div className="relative bg-[#FDFAF4] border border-[#E0D8C8] rounded-xl p-4 md:p-5 mb-3 md:mb-5 shadow-sm hover:shadow-md hover:-translate-y-[1px] transition-all overflow-hidden flex gap-3 md:gap-5 items-center group">
      {/* Left border gradient accent */}
      <div className="absolute left-0 top-0 bottom-0 w-[3px] md:w-[4px] bg-gradient-to-b from-[#0F3460] to-[#1A6B8A] rounded-l-sm" />
      
      {/* Date Box */}
      <div className="shrink-0 text-center bg-[#F5F0E6] p-2 md:p-3.5 rounded-lg text-[#5A4A3A] min-w-[4.6rem] md:min-w-[6.5rem] border border-[#EAE3D5]">
        <div className="text-[1.1rem] md:text-[1.4rem] font-bold leading-tight tracking-tight">{dayStr}</div>
        <div className="text-[0.85rem] md:text-[0.95rem] font-medium mt-1 text-[#8A8070]">{timeStr}</div>
      </div>

      {/* Content Area */}
      <div className="grow">
        <a href={item.link} target="_blank" rel="noopener noreferrer" className="block text-[0.92rem] md:text-[1.15rem] font-medium md:font-bold text-[#1A1A2E] leading-relaxed mb-1.5 md:mb-2 hover:text-[#1A6B8A] transition-colors">
          {item.title}
        </a>
        
        <div className="flex gap-2 items-center flex-wrap text-[0.65rem] md:text-[0.8rem] text-[#8A8070]">
          <span className={`px-2 py-0.5 md:py-1 md:px-3 rounded font-medium whitespace-nowrap ${getBadgeStyle(item.source_key)}`}>
            {item.source_emoji} {item.source_name}
          </span>
          {item.summary && (
            <details className="mt-1 w-full text-xs md:text-sm text-[#2A2A3E]">
              <summary className="cursor-pointer text-[#0F3460] font-medium py-1 hover:text-[#1A6B8A]">
                続きを読む
              </summary>
              <div className="bg-[#F7F3EC] p-3 md:p-4 rounded-lg border border-[#E0D8C8] mt-1 md:mt-2 leading-relaxed break-all" dangerouslySetInnerHTML={{ __html: item.summary }} />
            </details>
          )}
        </div>
      </div>
    </div>
  );
}
