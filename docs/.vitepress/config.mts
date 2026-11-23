import { defineConfig } from 'vitepress'

// 14 个模块页的侧边栏由 scripts/gen_module_pages.py 依据 modules.json 生成，
// 矩阵变更后跑 `npm run gen:modules` 即可重建，避免两处手工维护漂移。
import modulesNav from './modules-nav.json'

const repo = 'https://github.com/oagentkit'

export default defineConfig({
  lang: 'zh-CN',
  title: 'oagentkit',
  description: 'Agent / LLM 编排工具链模块矩阵 —— 14 个独立发版的 Go 模块',

  // 关闭 cleanUrls：站内链接一律带 .html，保证 /guide/ai-agent.html 这类
  // 完整文件名 URL 可直接命中（GitHub Pages 走静态文件，无 rewrite 兜底）。
  cleanUrls: false,
  lastUpdated: true,
  metaChunk: true,

  // 白 / 暗 / 自动三态（2026-11-23 改，与 kernel 站 / runtime 站同一套）。
  //
  // 写成对象而不是 true：valueLight 必须是显式的 'light'——默认值是空串，
  // 而空串在 VitePress 的预渲染脚本里等于「跟随系统」，表达不了「显式亮色」。
  // 三态入口由 theme/index.ts 挂在 nav-bar-content-after 槽位上。
  appearance: {
    valueDark: 'dark',
    valueLight: 'light'
  },

  // parts/ 下的是被 <!--@include:--> 注入首页的生成片段，不是独立页面。
  // 不排除的话它们会各自生成 .html 并混进 sitemap，搜索引擎会索引到残缺片段。
  srcExclude: ['parts/**'],

  head: [
    ['link', { rel: 'alternate', type: 'text/plain', href: '/llms.txt', title: 'llms.txt' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'oagentkit — Open Agent Kit' }],
    [
      'meta',
      {
        property: 'og:description',
        content: '14 个独立发版的 Go 模块，依赖严格自底向上，每仓独立 SemVer + 独立 CI。'
      }
    ]
  ],

  sitemap: { hostname: 'https://oagentkit.github.io' },

  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'oagentkit',

    nav: [
      { text: '指南', link: '/guide/getting-started', activeMatch: '/guide/' },
      { text: '模块', link: '/modules/textx', activeMatch: '/modules/' },
      // 坑速查提到顶栏一级：三站主导航同层（与 kernel 站 / runtime 站同一形状）。
      { text: '坑速查', link: '/reference/pitfalls' },
      // 站群配套链接：与 kernel 站 / runtime 站同一个入口、同一个标题。
      {
        text: 'AI 直读',
        items: [
          { text: '本站 llms.txt', link: '/llms.txt' },
          { text: 'kernel llms.txt', link: 'https://yi-nology.github.io/goagent-kernel/llms.txt' },
          { text: 'goagent-runtime llms.txt', link: 'https://yi-nology.github.io/goagent-runtime/llms.txt' },
          { text: 'oekit llms.txt', link: 'https://oekit.github.io/llms.txt' }
        ]
      },
      {
        text: '参考',
        items: [
          { text: '机器事实（模块 × 包 × 版本）', link: '/reference/packages' },
          // 版本矩阵是**机器可读 JSON**：人读的那一面在「机器事实」页，
          // 这里只留原始文件入口（.json 不在 VitePress 的已知扩展名里 ⇒
          // 客户端路由不拦截它，走整页导航拿到静态文件）。
          { text: '版本矩阵（机器可读 JSON）', link: '/versions.json' }
        ]
      },
      // 外链：VitePress 会自动加 ↗ 标记
      { text: 'oekit', link: 'https://oekit.github.io' },
      { text: 'GitHub', link: repo }
    ],

    sidebar: {
      '/guide/': [
        {
          text: '开始',
          items: [
            { text: '快速开始', link: '/guide/getting-started' },
            { text: '架构总览', link: '/guide/architecture' }
          ]
        },
        {
          text: '能力',
          items: [
            { text: 'AI Agent 编排', link: '/guide/ai-agent' },
            { text: '模型调用与路由', link: '/guide/llm-routing' },
            { text: '工具接入与治理', link: '/guide/tools-and-mcp' },
            { text: '可观测', link: '/guide/observability' }
          ]
        },
        {
          text: '升级',
          items: [{ text: '破坏性变更与升级指南', link: '/guide/breaking-changes' }]
        },
        {
          text: '参与',
          items: [{ text: 'CI 门禁与模块规则', link: '/guide/contributing' }]
        },
        {
          text: '姊妹项目',
          items: [{ text: 'oekit（Go 微服务工具链）', link: '/guide/oekit' }]
        }
      ],

      '/reference/': [
        {
          text: '参考',
          items: [
            { text: '机器事实（模块 × 包 × 版本）', link: '/reference/packages' },
            { text: '坑速查', link: '/reference/pitfalls' }
          ]
        }
      ],
      '/modules/': [
        { text: '模块总览', link: '/modules/' },
        {
          text: 'tier 0 · 基础层',
          items: modulesNav.filter((m) => m.tier === 0).map((m) => ({ text: m.repo, link: `/modules/${m.repo}` }))
        },
        {
          text: 'tier 1 · 能力层',
          items: modulesNav.filter((m) => m.tier === 1).map((m) => ({ text: m.repo, link: `/modules/${m.repo}` }))
        },
        {
          text: 'tier 2 · 集成层',
          items: modulesNav.filter((m) => m.tier === 2).map((m) => ({ text: m.repo, link: `/modules/${m.repo}` }))
        },
        {
          text: 'tier 3 · 编排层',
          items: modulesNav.filter((m) => m.tier === 3).map((m) => ({ text: m.repo, link: `/modules/${m.repo}` }))
        }
      ]
    },

    outline: { level: [2, 3], label: '本页目录' },
    search: { provider: 'local' },
    socialLinks: [{ icon: 'github', link: repo }],
    editLink: {
      pattern: `https://github.com/oagentkit/oagentkit.github.io/edit/main/docs/:path`,
      text: '在 GitHub 上编辑此页'
    },
    footer: {
      message: 'MIT License',
      copyright: 'oagentkit — Agent / LLM 编排工具链模块矩阵'
    }
  }
})
