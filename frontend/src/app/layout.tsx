import type { Metadata } from "next";
import Script from "next/script";
import { APP_NAME } from "@/constants";
import { Providers } from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: APP_NAME,
  description: "An AI-powered autonomous kitchen experience.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Grand+Hotel&family=Lato:wght@300;400;700;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Providers>{children}</Providers>
        {process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT ? (
          <Script
            strategy="afterInteractive"
            src={`${process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT}/umami`}
            data-website-id={process.env.NEXT_PUBLIC_ANALYTICS_WEBSITE_ID}
          />
        ) : null}
      </body>
    </html>
  );
}
