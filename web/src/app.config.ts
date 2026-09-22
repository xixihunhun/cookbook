export default defineAppConfig({
  pages: [
    "pages/index/index",       // 首页（闪购风格推荐）
    "pages/vote/vote",         // 每日抽签投票（核心页面）
    "pages/recipe/detail",     // 菜谱详情
    "pages/family/bind",       // 家庭绑定（创建/加入）
    "pages/family/mine",       // 我的家庭
    "pages/login/index",       // 登录
    "pages/mine/index",        // 我的
  ],
  window: {
    backgroundTextStyle: "light",
    navigationBarBackgroundColor: "#FF2D2D",
    navigationBarTitleText: "🍳 夫妻点菜",
    navigationBarTextStyle: "white",
    backgroundColor: "#FFF5F0",
  },
  tabBar: {
    color: "#999999",
    selectedColor: "#FF2D2D",
    backgroundColor: "#ffffff",
    borderStyle: "white",
    list: [
      {
        pagePath: "pages/index/index",
        text: "首页",
        iconPath: "assets/tab/home.png",
        selectedIconPath: "assets/tab/home_active.png",
      },
      {
        pagePath: "pages/vote/vote",
        text: "今日吃啥",
      },
      {
        pagePath: "pages/mine/index",
        text: "我的",
        iconPath: "assets/tab/mine.png",
        selectedIconPath: "assets/tab/mine_active.png",
      },
    ],
  },
});
