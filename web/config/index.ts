import path from "path";

const config: any = {
  projectName: "cookbook",
  date: "2026-9-22",
  designWidth: 750,
  deviceRatio: { 640: 2.34 / 2, 750: 1, 828: 1.81 / 2 },
  sourceRoot: "src",
  outputRoot: "dist",
  plugins: [],
  defineConstants: {},
  copy: { patterns: [], options: {} },
  framework: "vue3",
  compiler: "webpack5",
  cache: { enable: false },
  alias: {
    "@": path.resolve(__dirname, "..", "src"),
  },

  mini: {
    postcss: {
      pxtransform: { enable: true, config: {} },
      cssModules: { enable: false, config: { namingPattern: "module", generateScopedName: "[name]__[local]___[hash:base64:5]" } },
      url: { enable: true, config: { limit: 1024 } },
      cssnano: { enable: true, config: { autoprefixer: false } },
    },
  },

  h5: {
    publicPath: "/",
    staticDirectory: "static",
    postcss: {
      autoprefixer: { enable: true, config: {} },
      cssModules: { enable: false, config: { namingPattern: "module", generateScopedName: "[name]__[local]___[hash:base64:5]" } },
    },
    devServer: {
      proxy: {
        "/api": { target: "http://127.0.0.1:5000", changeOrigin: true },
      },
    },
  },
};

export default function (merge) {
  if (process.env.NODE_ENV === "development") {
    return merge({}, config, require("./dev").default);
  }
  return merge({}, config, require("./prod").default);
}
