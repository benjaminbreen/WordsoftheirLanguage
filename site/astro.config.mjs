import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import vercel from "@astrojs/vercel";

// Set SITE_URL in Vercel's environment once the domain is known.
export default defineConfig({
  site: process.env.SITE_URL || "https://wordes-of-their-language.vercel.app",
  trailingSlash: "never",
  build: { format: "file" },
  integrations: [sitemap()],
  prefetch: { prefetchAll: false, defaultStrategy: "hover" },
  adapter: vercel({
    webAnalytics: {
      enabled: true,
    },
  }),
});
