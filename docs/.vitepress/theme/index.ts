import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'

// 站点只做品牌色覆盖，功能沿用默认主题：
// 需要自定义组件（首页矩阵表之类）时再在这里 registerComponents。
import './custom.css'

export default {
  extends: DefaultTheme
} satisfies Theme
