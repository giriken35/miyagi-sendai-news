import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "仙台ニュース",
  description: "仙台ニュース巡回Webアプリ - StreamlitからVercelへ",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Noto+Serif+JP:wght@300;400;500;700&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased bg-[#F5F0E8]">
        {children}
      </body>
    </html>
  );
}
