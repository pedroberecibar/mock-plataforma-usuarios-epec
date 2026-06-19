import { defineConfig, mergeConfig } from "vite";
import baseConfig from "./vite.config";

// Build config for the GitHub Pages demo at:
// https://pedroberecibar.github.io/mock-plataforma-usuarios-epec/
//
// The regex alias redirects every ../api/<module> import to ../mock/<module>
// so no existing source file needs to be touched.
// api/types.ts is intentionally excluded — mock files import it directly.
export default mergeConfig(
  baseConfig,
  defineConfig({
    base: "/mock-plataforma-usuarios-epec/",
    resolve: {
      alias: [
        {
          find: /\/api\/(home|consumo|objetivos|factura|alertas|auth)/,
          replacement: "/mock/$1",
        },
      ],
    },
  })
);
