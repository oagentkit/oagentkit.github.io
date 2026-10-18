import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'

import DependencyGraph from './components/DependencyGraph.vue'
import OekitCard from './components/OekitCard.vue'
import './custom.css'

export default {
  extends: DefaultTheme,

  // 两个都踩过的坑，写在这里免得下次重蹈：
  //
  // 1. Layout 必须是**函数组件**。写成普通对象 `{ slots: {...} }` 会静默替换掉
  //    整个 Layout 组件 —— 构建照样报 success，但所有页面只剩 ~1.8KB 空壳，
  //    SSR 全站失效退化成纯客户端渲染。正确形态是 h(DefaultTheme.Layout, ...)。
  //
  // 2. h() 的第三个参数**本身就是槽对象**，槽名直接作 key。不要再套一层
  //    `{ slots: { ... } }` —— 那会造出一个名叫 `slots` 的槽，真槽名永远收不到。
  //
  // 槽挂在 sidebar-nav-after：侧边栏底部常驻姊妹项目入口，每一页都在，
  // 而不是只出现在提到 oekit 的那几页。Layout 会把该槽转发给 VPSidebar。
  Layout: () =>
    h(DefaultTheme.Layout, null, {
      'sidebar-nav-after': () => h(OekitCard)
    }),

  enhanceApp({ app }) {
    // 依赖关系图在 architecture.md 和首页都要用，注册成全局组件
    app.component('DependencyGraph', DependencyGraph)
  }
} satisfies Theme
