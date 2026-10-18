<script setup lang="ts">
/**
 * oagentkit 模块依赖关系图。
 *
 * 布局：tier 3 在顶、tier 0 在底，箭头由「依赖方」指向「被依赖方」——读作
 * 「上层坐在下层之上」，与矩阵「自底向上」的口径一致。分层由 tier 唯一决定，
 * 所以布局是确定的，不需要力导向。
 *
 * 纯计算渲染（无 DOM 访问），SSR 友好：不执行 JS 时 SVG 仍然完整可见，
 * 悬停高亮与链接是渐进增强。
 *
 * 数据来自 .vitepress/graph-data.json —— 由 scripts/gen_module_pages.py 从
 * data/modules.json 生成，与矩阵表共用同一份 INTRA_DEPS，两者不会漂移。
 */
import { computed, ref } from 'vue'
import graphData from '../../graph-data.json'

interface GraphNode {
  repo: string
  tier: number
  desc: string
  packages: number
  eino: boolean
  href: string
}
interface GraphEdge {
  from: string
  to: string
}

const NODE_W = 138
const NODE_H = 46
const H_GAP = 16
const V_GAP = 96
const PAD_L = 118
const PAD_R = 26
const PAD_T = 18
const PAD_B = 18

const nodes = (graphData as { nodes: GraphNode[] }).nodes
const edges = (graphData as { edges: GraphEdge[] }).edges
const tiers = (graphData as { tiers: { tier: number; label: string; desc: string }[] }).tiers
const dependents = (graphData as { dependents: Record<string, string[]> }).dependents

// 同一层内按需排列：让连线尽量短、尽量不交叉 —— 边数少的放中间优先。
const rows = computed(() =>
  tiers.map((t) => ({
    ...t,
    nodes: nodes.filter((n) => n.tier === t.tier)
  }))
)

const contentW = computed(() => {
  const max = Math.max(...rows.value.map((r) => r.nodes.length))
  return max * NODE_W + (max - 1) * H_GAP
})
const width = PAD_L + contentW.value + PAD_R
const height = PAD_T + rows.value.length * NODE_H + (rows.value.length - 1) * V_GAP + PAD_B

const pos = computed(() => {
  const map: Record<string, { x: number; y: number; cx: number; cy: number }> = {}
  rows.value.forEach((row, rowIndex) => {
    const rowW = row.nodes.length * NODE_W + (row.nodes.length - 1) * H_GAP
    const left = PAD_L + (contentW.value - rowW) / 2
    const y = PAD_T + rowIndex * (NODE_H + V_GAP)
    row.nodes.forEach((n, i) => {
      const x = left + i * (NODE_W + H_GAP)
      map[n.repo] = { x, y, cx: x + NODE_W / 2, cy: y + NODE_H / 2 }
    })
  })
  return map
})

// 依赖方 → 被依赖方；控制点在竖直方向，跨层时走平滑曲线。
const paths = computed(() =>
  edges
    .filter((e) => pos.value[e.from] && pos.value[e.to])
    .map((e) => {
      const a = pos.value[e.from]
      const b = pos.value[e.to]
      const dy = (b.y - (a.y + NODE_H)) / 2
      return {
        ...e,
        d: `M ${a.cx} ${a.y + NODE_H} C ${a.cx} ${a.y + NODE_H + dy} ${b.cx} ${b.y - dy} ${b.cx} ${b.y}`
      }
    })
)

const hover = ref<string | null>(null)

const depsOf = (repo: string) => edges.filter((e) => e.from === repo).map((e) => e.to)
const dependentsOf = (repo: string) => dependents[repo] ?? []

// 悬停某模块时连带点亮它的直接依赖方与被依赖方，其余淡出。
const related = computed(() => {
  if (!hover.value) return null
  return new Set<string>([
    hover.value,
    ...depsOf(hover.value),
    ...dependentsOf(hover.value)
  ])
})

const nodeDim = (repo: string) => !!related.value && !related.value!.has(repo)
const edgeActive = (e: GraphEdge) => hover.value === e.from || hover.value === e.to

const edgeStroke = (e: GraphEdge) => {
  if (!related.value) return 'var(--dg-edge)'
  return edgeActive(e) ? 'var(--dg-edge-active)' : 'var(--dg-edge-dim)'
}
const edgeMarker = (e: GraphEdge) => {
  if (!related.value) return 'url(#dg-arrow)'
  return edgeActive(e) ? 'url(#dg-arrow-active)' : 'url(#dg-arrow-dim)'
}

const nodeState = (repo: string) => {
  if (!related.value) return 'idle'
  if (repo === hover.value) return 'self'
  return 'related'
}

const focusDetail = computed(() => {
  const repo = hover.value
  if (!repo) return null
  const n = nodes.find((x) => x.repo === repo)!
  const d = depsOf(repo)
  const up = dependentsOf(repo)
  return {
    repo,
    desc: n.desc,
    packages: n.packages,
    eino: n.eino,
    deps: d,
    dependents: up
  }
})
</script>

<template>
  <div class="dg" @mouseleave="hover = null">
    <div class="dg-head">
      <span class="dg-hint">悬停看依赖 · 点击进模块页</span>
      <span v-if="focusDetail" class="dg-detail">
        <strong>{{ focusDetail.repo }}</strong>
        <span class="dg-desc">{{ focusDetail.desc }}</span>
        <span class="dg-relation">
          依赖
          <template v-if="focusDetail.deps.length">
            <a v-for="d in focusDetail.deps" :key="d" :href="`/modules/${d}.html`" @mouseenter="hover = d">{{ d }}</a>
          </template>
          <em v-else>无</em>
        </span>
        <span class="dg-relation">
          被依赖
          <template v-if="focusDetail.dependents.length">
            <a v-for="d in focusDetail.dependents" :key="d" :href="`/modules/${d}.html`" @mouseenter="hover = d">{{ d }}</a>
          </template>
          <em v-else>无（矩阵叶子）</em>
        </span>
      </span>
    </div>

    <div class="dg-scroll">
      <svg
        class="dg-svg"
        :viewBox="`0 0 ${width} ${height}`"
        :width="width"
        :height="height"
        role="img"
        aria-label="oagentkit 模块依赖关系图：13 个模块按 tier 0 到 3 分四层，箭头指向被依赖的模块"
      >
        <defs>
          <marker id="dg-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="var(--dg-edge)" />
          </marker>
          <marker id="dg-arrow-active" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="var(--dg-edge-active)" />
          </marker>
          <marker id="dg-arrow-dim" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 9 5 L 0 9 z" fill="var(--dg-edge-dim)" />
          </marker>
        </defs>

        <!-- 层带与层名 -->
        <g v-for="(row, i) in rows" :key="row.tier">
          <rect
            class="dg-band"
            :x="PAD_L - 14"
            :y="PAD_T + i * (NODE_H + V_GAP) - 10"
            :width="contentW + 28"
            :height="NODE_H + 20"
            rx="10"
          />
          <text class="dg-tier" :x="PAD_L - 26" :y="PAD_T + i * (NODE_H + V_GAP) + NODE_H / 2 - 2">
            {{ row.label }}
          </text>
          <text class="dg-tier-sub" :x="PAD_L - 26" :y="PAD_T + i * (NODE_H + V_GAP) + NODE_H / 2 + 14">
            {{ row.desc }}
          </text>
        </g>

        <!-- 边在节点之下 -->
        <path
          v-for="e in paths"
          :key="`${e.from}-${e.to}`"
          class="dg-edge"
          :class="{ dim: related && !edgeActive(e) }"
          :d="e.d"
          :style="{ stroke: edgeStroke(e), markerEnd: edgeMarker(e) }"
        />

        <!-- 节点 -->
        <a
          v-for="n in nodes"
          :key="n.repo"
          :href="n.href"
          class="dg-node-link"
          @mouseenter="hover = n.repo"
          @focus="hover = n.repo"
        >
          <g
            class="dg-node"
            :class="[`is-${nodeState(n.repo)}`, { dim: nodeDim(n.repo) }]"
            :transform="`translate(${pos[n.repo].x} ${pos[n.repo].y})`"
          >
            <rect class="dg-node-box" :width="NODE_W" :height="NODE_H" rx="9" />
            <text class="dg-repo" :x="NODE_W / 2" :y="n.eino ? 20 : NODE_H / 2 + 5">{{ n.repo }}</text>
            <text v-if="n.eino" class="dg-meta" :x="NODE_W / 2" :y="36">{{ n.packages }} 包 · eino</text>
            <text v-else class="dg-meta" :x="NODE_W / 2" :y="NODE_H / 2 + 21">{{ n.packages }} 包</text>
            <circle v-if="n.eino" class="dg-eino-dot" :cx="NODE_W - 13" cy="13" r="3.5" />
          </g>
        </a>
      </svg>
    </div>

    <div class="dg-legend">
      <span><i class="sw sw-plain" />纯 Go 模块</span>
      <span><i class="sw sw-eino" />直接依赖 eino（框架层）</span>
      <span class="dg-legend-note">箭头方向 = 依赖方 → 被依赖方 · tier N 不得依赖 tier &gt; N</span>
    </div>
  </div>
</template>

<style scoped>
.dg {
  margin: 1.5rem 0 2rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  padding: 14px 16px 12px;
  --dg-edge: #b6c2d4;
  --dg-edge-active: var(--vp-c-brand-1);
  --dg-edge-dim: #e6eaf0;
  --dg-node-bg: var(--vp-c-bg);
  --dg-node-br: var(--vp-c-divider);
}

.dark .dg {
  --dg-edge: #46536b;
  --dg-edge-active: var(--vp-c-brand-1);
  --dg-edge-dim: #232b38;
  --dg-node-bg: #161b22;
  --dg-node-br: #30363d;
}

.dg-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px 14px;
  min-height: 22px;
  margin-bottom: 6px;
  font-size: 13px;
}

.dg-hint {
  color: var(--vp-c-text-3);
  flex: none;
}

.dg-detail {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 4px 10px;
  color: var(--vp-c-text-2);
}

.dg-detail strong {
  font-family: var(--vp-font-family-mono);
  color: var(--vp-c-brand-1);
  font-size: 14px;
}

.dg-desc {
  color: var(--vp-c-text-3);
}

.dg-relation {
  color: var(--vp-c-text-3);
}

.dg-relation a {
  font-family: var(--vp-font-family-mono);
  font-size: 12px;
  margin-right: 6px;
  text-decoration: none;
  border-bottom: 1px dashed currentColor;
}

.dg-relation em {
  font-style: normal;
  opacity: 0.7;
}

.dg-scroll {
  overflow-x: auto;
  overflow-y: hidden;
}

.dg-svg {
  display: block;
  margin: 0 auto;
  /* 标准响应式 SVG：width/height 属性给自然尺寸，max-width 负责按容器等比缩小
     （height:auto 由 viewBox 推出）。窄于 480px 才转为横向滚动，避免节点挤成一团。 */
  max-width: 100%;
  height: auto;
  min-width: 480px;
}

.dg-band {
  fill: var(--vp-c-bg);
  opacity: 0.5;
  stroke: var(--vp-c-divider);
  stroke-width: 1;
  stroke-dasharray: 3 4;
}

.dark .dg-band {
  opacity: 0.35;
}

.dg-tier {
  fill: var(--vp-c-text-2);
  font-size: 12px;
  font-weight: 600;
  text-anchor: end;
}

.dg-tier-sub {
  fill: var(--vp-c-text-3);
  font-size: 9.5px;
  text-anchor: end;
}

.dg-edge {
  fill: none;
  stroke-width: 1.5;
  transition: stroke 0.15s ease, opacity 0.15s ease;
}

.dg-edge.dim {
  opacity: 0.55;
}

.dg-node {
  transition: opacity 0.15s ease;
  cursor: pointer;
}

.dg-node.dim {
  opacity: 0.28;
}

.dg-node-box {
  fill: var(--dg-node-bg);
  stroke: var(--dg-node-br);
  stroke-width: 1.5;
  transition: stroke 0.15s ease, stroke-width 0.15s ease;
}

.dg-node.is-related .dg-node-box {
  stroke: var(--vp-c-brand-1);
}

.dg-node.is-self .dg-node-box {
  stroke: var(--vp-c-brand-1);
  stroke-width: 2.5;
  fill: var(--vp-c-brand-soft);
}

.dg-repo {
  fill: var(--vp-c-text-1);
  font-family: var(--vp-font-family-mono);
  font-size: 15px;
  font-weight: 600;
  text-anchor: middle;
}

.dg-meta {
  fill: var(--vp-c-text-3);
  font-size: 10px;
  text-anchor: middle;
}

.dg-eino-dot {
  fill: var(--vp-c-brand-1);
  opacity: 0.75;
}

.dg-node-link:focus-visible .dg-node-box {
  stroke: var(--vp-c-brand-1);
  stroke-width: 2.5;
}

.dg-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 16px;
  margin-top: 10px;
  padding-top: 9px;
  border-top: 1px solid var(--vp-c-divider);
  font-size: 12px;
  color: var(--vp-c-text-3);
}

.dg-legend span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.sw {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  display: inline-block;
}

.sw-plain {
  background: transparent;
  border: 1.5px solid var(--vp-c-text-3);
}

.sw-eino {
  background: var(--vp-c-brand-1);
  opacity: 0.75;
}

.dg-legend-note {
  margin-left: auto;
}

@media (max-width: 640px) {
  .dg-legend-note {
    margin-left: 0;
  }
}
</style>
