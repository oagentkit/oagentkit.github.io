import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'

import DependencyGraph from './components/DependencyGraph.vue'
import './custom.css'

// 依赖关系图在 architecture.md 和首页都要用，注册成全局组件
export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('DependencyGraph', DependencyGraph)
  }
} satisfies Theme
