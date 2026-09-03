"use client";

import { useEffect, useState, useMemo } from "react";
import NewsCard, { NewsItem } from "@/components/NewsCard";
import { categorizeItem, CATEGORY_LABELS } from "@/utils/categories";

export default function Home() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    // Fetch directly from GitHub raw to bypass Vercel build process
    fetch("https://raw.githubusercontent.com/giriken35/miyagi-sendai-news/main/news_data.json?t=" + new Date().getTime())
      .then(res => res.json())
      .then(data => {
        const itemsArray = data.items || [];
        // Sort and map fields to match NewsItem interface
        const sorted = itemsArray.sort((a: any, b: any) => b.pub_ts - a.pub_ts);
        const categorized = sorted.map((item: any) => ({
          ...item,
          published: new Date(item.pub_ts * 1000).toISOString(),
          source_name: item.source,
          source_emoji: item.emoji,
          category: categorizeItem(item.title + " " + (item.summary || ""))
        }));
        setNews(categorized);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load news", err);
        setLoading(false);
      });
  }, []);

  const counts = useMemo(() => {
    const counts: Record<string, number> = { all: news.length };
    Object.keys(CATEGORY_LABELS).forEach(cat => {
      if (cat !== "all") counts[cat] = 0;
    });
    news.forEach(item => {
      if (item.category && counts[item.category] !== undefined) {
        counts[item.category]++;
      } else {
        counts.general = (counts.general || 0) + 1;
      }
    });
    return counts;
  }, [news]);

  const filteredNews = news.filter(n => {
    const matchesTab = activeTab === "all" || n.category === activeTab;
    const matchesSearch = searchQuery === "" || 
      n.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (n.summary && n.summary.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesTab && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-[#F5F0E8] text-[#1A1A2E] font-serif pb-12">
      <div className="max-w-[960px] mx-auto px-4 pt-2">
        {/* Header */}
        <header className="bg-gradient-to-br from-[#1A1A2E] via-[#16213E] to-[#0F3460] text-[#E8D5B0] p-6 rounded-b-[18px] -mx-4 mb-6 text-center shadow-lg">
          <h1 className="text-[1.6rem] font-bold tracking-wider leading-tight m-0">仙台ニュース</h1>
          <p className="font-sans text-[0.72rem] text-[#A09070] mt-1 tracking-widest">SENDAI NEWS - 河北新報 / 仙台つーしん / Yahoo!宮城</p>
        </header>

        {/* Tabs */}
        <div className="bg-[#EDE8DC] p-1 rounded-xl mb-6 shadow-inner flex flex-wrap gap-1">
          {Object.entries(CATEGORY_LABELS).map(([key, { label, emoji }]) => {
            const count = counts[key] || 0;
            const isActive = activeTab === key;
            return (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`font-sans text-[0.78rem] md:text-[0.9rem] font-medium py-1.5 px-2.5 md:py-2 md:px-3 rounded-lg transition-all flex-grow-0
                  ${isActive 
                    ? 'bg-[#1A1A2E] text-[#E8D5B0] shadow-md' 
                    : 'text-[#5A5A6A] hover:bg-white/50'}`}
              >
                {emoji} {label} ({count})
              </button>
            );
          })}
        </div>

        {/* Search Bar */}
        <div className="mb-6 bg-[#EDE8DC] p-2.5 md:p-3 rounded-xl shadow-inner flex items-center gap-2">
          <span className="text-[#8A8070] text-[1.1rem] md:text-[1.3rem] pl-2">🔍</span>
          <span className="text-[#8A8070] font-sans text-[0.8rem] md:text-[0.95rem] whitespace-nowrap hidden sm:inline">全記事からキーワードで検索</span>
          <input
            type="text"
            placeholder="例: 紫区、お祭り、火事..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent border-none outline-none text-[#1A1A2E] placeholder-[#A09070] font-sans text-[0.85rem] md:text-[1rem] px-1 md:px-2"
          />
        </div>

        {/* Content */}
        {loading ? (
          <div className="text-center py-12 text-[#8A8070] font-sans">
            <div className="animate-spin inline-block w-6 h-6 border-[3px] border-current border-t-transparent text-[#0F3460] rounded-full mb-3" />
            <p>ニュースを読み込んでいます...</p>
          </div>
        ) : filteredNews.length > 0 ? (
          <div className="space-y-3">
            {filteredNews.map((item, idx) => (
              <NewsCard key={idx} item={item} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-[#8A8070] font-sans">
            記事が見つかりませんでした。
          </div>
        )}

      </div>
    </div>
  );
}
