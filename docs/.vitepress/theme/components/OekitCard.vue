<script setup lang="ts">
/**
 * 侧边栏常驻的姊妹项目入口（oagentkit.github.io）。
 *
 * 挂在默认主题的 sidebar-nav-after 插槽里，所以在每一页的侧边栏底部都在。
 * oagentkit 与 oekit 是两套独立矩阵，这里是唯一一处把「去看 oekit」放在
 * 随手可见的位置——其余页面只是正文里偶尔提到。
 *
 * 全部外链走 rel="noopener"，并标注「独立矩阵」避免读者误以为是子品牌。
 */
const links = [
  { label: '文档站', href: 'https://oekit.github.io' },
  { label: 'llms.txt', href: 'https://oekit.github.io/llms.txt' },
  { label: 'GitHub', href: 'https://github.com/oekit' }
]
</script>

<template>
  <div class="ok-card">
    <div class="ok-head">
      <span class="ok-kicker">姊妹项目</span>
      <a class="ok-title" href="https://oekit.github.io" target="_blank" rel="noopener">
        oekit <span class="ok-ext" aria-hidden="true">↗</span>
      </a>
      <p class="ok-desc">Open Easy Kit · Go 微服务工具链</p>
    </div>

    <ul class="ok-links">
      <li v-for="l in links" :key="l.href">
        <a :href="l.href" target="_blank" rel="noopener">
          {{ l.label }} <span class="ok-ext" aria-hidden="true">↗</span>
        </a>
      </li>
    </ul>

    <p class="ok-note">
      两套<b>独立</b>矩阵，不是子品牌。本站依赖它的
      <code>pkg</code> / <code>concurrency</code> / <code>logx</code>。
    </p>
  </div>
</template>

<style scoped>
.ok-card {
  margin: 18px 12px 20px;
  padding: 11px 12px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
  font-size: 12px;
  line-height: 1.55;
}

.ok-kicker {
  display: block;
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--vp-c-text-3);
}

.ok-title {
  display: inline-block;
  margin: 2px 0 0;
  font-family: var(--vp-font-family-mono);
  font-size: 14px;
  font-weight: 600;
  color: var(--vp-c-brand-1);
  text-decoration: none;
}

.ok-title:hover {
  text-decoration: underline;
}

.ok-ext {
  font-size: 0.85em;
  opacity: 0.7;
}

.ok-desc {
  margin: 2px 0 8px;
  color: var(--vp-c-text-2);
  font-size: 11.5px;
}

.ok-links {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
  margin: 0 0 8px;
  padding: 0;
  list-style: none;
}

.ok-links a {
  color: var(--vp-c-text-2);
  text-decoration: none;
  border-bottom: 1px solid var(--vp-c-divider);
}

.ok-links a:hover {
  color: var(--vp-c-brand-1);
  border-bottom-color: var(--vp-c-brand-1);
}

.ok-note {
  margin: 0;
  padding-top: 8px;
  border-top: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-3);
  font-size: 11px;
}

.ok-note code {
  font-family: var(--vp-font-family-mono);
  font-size: 10.5px;
  padding: 0 3px;
  border-radius: 3px;
  background: var(--vp-c-default-soft);
}
</style>
