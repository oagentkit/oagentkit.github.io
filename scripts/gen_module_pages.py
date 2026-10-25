#!/usr/bin/env python3
"""
由 data/modules.json 生成 oagentkit 文档站的模块页、侧边栏与首页矩阵表。

单一数据源：data/modules.json（从 matrix-tools 仓同步而来，schema 同源）。
仓间依赖直接读 modules.json 的 dependsOn 字段（缺字段 = 零依赖），
不另维护第二份 —— 图、矩阵表、模块页与权威数据因此不可能漂移。

用法：
    npm run gen:modules
    python3 scripts/gen_module_pages.py --check     # 只校验是否已是最新，不写文件
"""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "modules.json"
DOCS = ROOT / "docs"
NAV_OUT = DOCS / ".vitepress" / "modules-nav.json"
GRAPH_OUT = DOCS / ".vitepress" / "graph-data.json"
MODULES_OUT = DOCS / "modules"
PARTS_OUT = DOCS / "parts"

ORG = "https://github.com/oagentkit"

TIER_LABEL = {
    0: "tier 0 · 基础层",
    1: "tier 1 · 能力层",
    2: "tier 2 · 集成层",
    3: "tier 3 · 编排层",
}

TIER_DESC = {
    0: "零仓内依赖或仅依赖同仓包",
    1: "依赖 tier 0",
    2: "依赖 tier 0/1 + 重第三方地板",
    3: "依赖 llm 等 tier 2 门面",
}

# 仓间依赖（intra-matrix）读 modules.json 的 dependsOn 字段，不再在本文件维护。
#
# 之前这里硬编码过一份 INTRA_DEPS，那是手抄的第二份依赖数据 —— 退役/新增模块时
# 极易与 modules.json 漂移（breaker 退役时就真漂了：llm 不再依赖 runtime，
# 手抄表还留着）。dependsOn 缺字段 = 零仓内依赖（tier 0 即如此）。
def deps_of(module):
    return module.get("dependsOn") or []


def load():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    mods = sorted(data["modules"], key=lambda m: (m["tier"], m["repo"]))
    return data, mods


def reverse_deps(mods):
    """repo -> 直接依赖它的仓列表。"""
    rev = {m["repo"]: [] for m in mods}
    for m in mods:
        for dep in deps_of(m):
            if dep in rev:
                rev[dep].append(m["repo"])
    return rev


def compat_by_repo(data):
    """账本里 kind == "compat" 的条目按仓归组（过渡期兼容镜像）。

    账本（data/modules.json 的 retiringPackages）混着两种东西：
      - kind == "retired"：已退役的包（breaker）—— 那条路径已经没了；
      - kind == "compat" ：过渡期兼容镜像（llm/llm）—— **路径仍然可用**。

    两者必须分开渲染。把「活着的」按「已退役」渲染，会在**对外公开的站点**上
    写出假陈述：「已从本矩阵移出」/ issue 链指向别的仓 / 交叉引用指向别的模块。
    """
    out = {}
    for entry in data.get("retiringPackages") or []:
        if entry.get("kind") == "compat" and entry.get("repo"):
            out.setdefault(entry["repo"], []).append(entry)
    return out


def issue_links(entry):
    """账本条目的需求链 → Markdown 列表行。

    issue 仓**必须由数据决定**：以前这里硬编码成 oekit/concurrency ——
    换个仓的需求链（如 llm/llm 的需求链在 oagentkit/llm）就会渲染出
    指向别处的假链接。缺字段时回落到旧硬编码值，老记录的渲染逐字节不变。
    """
    chain = entry.get("issueChain") or {}
    if not chain:
        return []
    repo = entry.get("issueRepo") or "oekit/concurrency"
    rows = []
    for num, desc in chain.items():
        rows.append(f"  - [`#{num}`](https://github.com/{repo}/issues/{num}) —— {desc}")
    return rows


def mod_link(repo, text=None):
    return f"[`{repo}`](/modules/{repo}.html){text or ''}"


def render_matrix_table(mods):
    rows = [
        "| 模块 | 层 | 说明 | 仓内依赖 |",
        "| --- | --- | --- | --- |",
    ]
    for m in mods:
        deps = deps_of(m)
        deps_cell = "、".join(f"`{d}`" for d in deps) if deps else "—"
        rows.append(
            f"| [`{m['repo']}`](/modules/{m['repo']}.html) "
            f"| <span class=\"matrix-tier\">tier {m['tier']}</span> "
            f"| {m['ghDescription']} "
            f"| <span class=\"matrix-tier\">{deps_cell}</span> |"
        )
    return "\n".join(rows) + "\n"


def render_module_page(m, rev, import_root, compat=()):
    repo = m["repo"]
    deps = deps_of(m)
    rdeps = rev.get(repo, [])
    lines = []

    lines.append(f"# {repo}")
    lines.append("")
    lines.append(m["ghDescription"])
    lines.append("")

    lines.append("## 概况")
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("| --- | --- |")
    lines.append(f"| 层 | {TIER_LABEL[m['tier']]}（{TIER_DESC[m['tier']]}） |")
    lines.append(f"| oekit 对应 | `{m['oekitAnalog']}` |")
    lines.append(
        f"| 仓内依赖 | {'、'.join(f'`{d}`' for d in deps) if deps else '—（零仓内依赖）'} |"
    )
    lines.append(
        f"| 被依赖 | {'、'.join(f'`{d}`' for d in rdeps) if rdeps else '—（矩阵叶子）'} |"
    )
    heavy = m.get("heavyDeps") or []
    lines.append(f"| 第三方地板 | {'、'.join(f'`{d}`' for d in heavy) if heavy else '零'} |")
    lines.append(f"| 包数 | {len(m['packages'])} |")
    lines.append("")

    lines.append("## 安装")
    lines.append("")
    lines.append("```bash")
    lines.append(f"go get {import_root}/{repo}@latest")
    lines.append("```")
    lines.append("")
    lines.append(f"源码与该仓 `AGENTS.md`：[oagentkit/{repo}]({ORG}/{repo})")
    lines.append("")

    lines.append("## 包")
    lines.append("")
    lines.append("| 包 | 说明 |")
    lines.append("| --- | --- |")
    pkg_desc = m.get("pkgDesc") or {}
    for p in m["packages"]:
        lines.append(f"| `{p}` | {pkg_desc.get(p, '')} |")
    lines.append("")

    # 过渡期兼容镜像：**不在**上面的规范包清单里（它进清单会让 versions.json
    # 给两个包登记同一个 importPath），但路径仍然可用 —— 存量下游还钉在上面。
    if compat:
        lines.append("## 过渡期兼容镜像")
        lines.append("")
        for cp in compat:
            lines.append(f"- `{cp.get('pkg', '?')}`")
            if cp.get("impl"):
                lines.append(f"  - 实现：{cp['impl']}")
            if cp.get("importPath"):
                lines.append(
                    f"  - 可用 import 路径：`{cp['importPath']}`（{cp.get('availableIn', '—')}）"
                )
            if cp.get("canonicalPath"):
                lines.append(f"  - 规范路径：`{cp['canonicalPath']}` —— 新代码用它")
            if cp.get("whyNotInPackages"):
                lines.append(f"  - 不进规范包清单的原因：{cp['whyNotInPackages']}")
            if cp.get("status"):
                lines.append(f"  - 状态：{cp['status']}")
            if cp.get("plan"):
                lines.append(f"  - 下一步：{cp['plan']}")
        lines.append("")

    lines.append("## 本仓硬规则")
    lines.append("")
    lines.append(
        "以下约束出自该仓 `AGENTS.md`。**改代码前先读仓库根目录的 `AGENTS.md`**，"
        "此处是摘要，不是替代。"
    )
    lines.append("")
    lines.append(m["agentNotes"].strip())
    lines.append("")

    lines.append("## 日志约定")
    lines.append("")
    lines.append(m["loggingRule"].strip())
    lines.append("")

    lines.append("## 相关")
    lines.append("")
    lines.append("- [架构总览](/guide/architecture.html) —— 分层不变量与依赖方向")
    if repo in ("agent", "llm", "runtime", "promptx", "toolgate"):
        lines.append("- [AI Agent 编排](/guide/ai-agent.html)")
    if repo in ("llm", "obs", "runtime"):
        lines.append("- [模型调用与路由](/guide/llm-routing.html)")
    if repo in ("mcpkit", "toolgate", "tools", "guardx"):
        lines.append("- [工具接入与治理](/guide/tools-and-mcp.html)")
    if repo in ("obs", "llm"):
        lines.append("- [可观测](/guide/observability.html)")
    lines.append("")

    return "\n".join(lines)


def render_compat_section(cp):
    """账本里 kind == "compat" 的条目 → 索引页的一段。

    这一段的每句话都必须为真：它是**活着的**兼容镜像，
    不是「已从本矩阵移出」的包 —— 存量下游还钉在这条路径上。
    """
    pkg = cp.get("pkg", "?")
    repo = cp.get("repo", "?")
    lines = []
    lines.append(f"## 过渡期兼容镜像：{pkg}")
    lines.append("")
    lines.append(
        f"`{pkg}` 是 `{repo}` 仓的**过渡期兼容镜像**——把根包的导出符号镜像过来"
        "（类型别名 / 函数转发 / 常量转发），**不含任何自己的实现**，只为存量下游存在。"
    )
    lines.append("")
    if cp.get("impl"):
        lines.append(f"- 实现：{cp['impl']}")
    if cp.get("importPath"):
        lines.append(
            f"- 可用 import 路径：`{cp['importPath']}`（{cp.get('availableIn', '—')}）"
        )
    if cp.get("canonicalPath"):
        lines.append(f"- 规范路径：`{cp['canonicalPath']}` —— 矩阵的规范包清单只登记它")
    if cp.get("whyNotInPackages"):
        lines.append(f"- 不进规范包清单的原因：{cp['whyNotInPackages']}")
    if cp.get("issueChain"):
        lines.append("- 相关 issue（已关闭）：")
        lines.extend(issue_links(cp))
    if cp.get("status"):
        lines.append(f"- 状态：{cp['status']}")
    if cp.get("plan"):
        lines.append(f"- 下一步：{cp['plan']}")
    lines.append("")
    # 交叉引用的模块由数据决定（缺字段回落到该条目所属仓）
    timeline = cp.get("timelineModule") or repo
    lines.append(
        f"完整说明见 [`{timeline}` 模块页](/modules/{timeline}.html) 的「过渡期兼容镜像」段。"
    )
    lines.append("")
    return lines


def render_modules_index(data, mods):
    rev = reverse_deps(mods)
    lines = []
    lines.append("# 模块总览")
    lines.append("")
    lines.append(
        f"oagentkit 是 **{len(mods)} 个独立发版的 Go 模块**，依赖严格自底向上，"
        "每仓独立 SemVer + 独立 CI。"
    )
    lines.append("")
    lines.append("> 每个仓库根目录都有 `AGENTS.md` —— 面向 AI Agent 的权威规范与硬规则。")
    lines.append("")

    for tier in (0, 1, 2, 3):
        group = [m for m in mods if m["tier"] == tier]
        if not group:
            continue
        lines.append(f"## {TIER_LABEL[tier]}")
        lines.append("")
        lines.append(f"*{TIER_DESC[tier]}*")
        lines.append("")
        lines.append("| 模块 | 说明 | 仓内依赖 |")
        lines.append("| --- | --- | --- |")
        for m in group:
            deps = deps_of(m)
            deps_cell = "、".join(f"`{d}`" for d in deps) if deps else "—"
            lines.append(
                f"| [`{m['repo']}`](/modules/{m['repo']}.html) "
                f"| {m['desc']} | <span class=\"matrix-tier\">{deps_cell}</span> |"
            )
        lines.append("")

    lines.append("## 基建仓")
    lines.append("")
    lines.append("| 仓 | 角色 |")
    lines.append("| --- | --- |")
    for ir in data.get("infraRepos", []):
        lines.append(f"| [`{ir['repo']}`]({ORG}/{ir['repo']}) | {ir['role']} |")
    lines.append("")

    # 账本（retiringPackages）里混着两种东西，必须分开渲染：
    #   kind == "compat" → 过渡期兼容镜像：**路径仍然可用**；
    #   其它             → 已退役的包（那条路径已经没了）。
    # 兼容镜像排前面：扫索引的人先看到「还能用的路径」，再看到历史。
    ledger = data.get("retiringPackages") or []
    for cp in [e for e in ledger if e.get("kind") == "compat"]:
        lines.extend(render_compat_section(cp))
    for rp in [e for e in ledger if e.get("kind") != "compat"]:
        pkg = rp.get("pkg", "?")
        repl = rp.get("replacement")
        lines.append(f"## 已退役的包：{pkg}")
        lines.append("")
        if repl:
            lines.append(
                f"`{pkg}` 已从本矩阵移出，迁往 `{repl}`。**退役是分阶段完成的**——"
                "消费方先改依赖上游、上游能力补齐，最后才删包，"
                "任何一步提前做都是构建断裂。"
            )
            lines.append("")
        if rp.get("consumedBy"):
            lines.append(f"- 消费方：{rp['consumedBy']}")
        chain = rp.get("issueChain") or {}
        if chain:
            lines.append("- 上游需求链（全部已关闭）：")
            lines.extend(issue_links(rp))
        # 退役记录有两种终局写法：退役未完成时用 action（下一步做什么），
        # 退役完成后用 status（终局是什么）。两者都渲染，别因为换键就整段丢。
        if rp.get("status"):
            lines.append(f"- 状态：{rp['status']}")
        if rp.get("action"):
            lines.append(f"- 后续：{rp['action']}")
        lines.append("")
        # 交叉引用的模块由数据决定（缺字段回落旧硬编码值 ⇒ 老记录逐字节不变）
        timeline = rp.get("timelineModule") or "runtime"
        lines.append(
            f"退役完整时间线见 [`{timeline}` 模块页](/modules/{timeline}.html) 的「本仓硬规则」。"
        )
        lines.append("")

    if data.get("droppedPackages"):
        lines.append("## 已移除的包")
        lines.append("")
        for dp in data["droppedPackages"]:
            if isinstance(dp, dict):
                pkg = dp.get("pkg", dp.get("package", "?"))
                why = dp.get("reason") or dp.get("note", "")
                lines.append(f"- `{pkg}` —— {why}")
            else:
                lines.append(f"- {dp}")
        lines.append("")

    lines.append("## 相关")
    lines.append("")
    lines.append("- [快速开始](/guide/getting-started.html)")
    lines.append("- [架构总览](/guide/architecture.html)")
    lines.append("- [CI 门禁与模块规则](/guide/contributing.html)")
    lines.append("")
    return "\n".join(lines)


def render_graph_data(data, mods, rev):
    """依赖关系图的数据源。

    与页面共用 modules.json 的 dependsOn，所以图和矩阵表永远一致 —— 手改其中一处，
    另一处下次生成时就跟上了，不会出现「图说 A 依赖 B、表说 A 不依赖 B」。

    tier 3 在顶部、tier 0 在底部：箭头由依赖方向（依赖方 → 被依赖方）向下指，
    读起来就是「上层坐在下层之上」，与「自底向上」的口径一致。
    """
    nodes = []
    for m in mods:
        nodes.append(
            {
                "repo": m["repo"],
                "tier": m["tier"],
                "desc": m["desc"],
                "packages": len(m["packages"]),
                # eino 是本矩阵的「框架层」，标出来以便一眼看出耦合面
                "eino": any("cloudwego/eino" in d for d in (m.get("heavyDeps") or [])),
                "href": f"/modules/{m['repo']}.html",
            }
        )

    edges = []
    for m in mods:
        for dep in deps_of(m):
            edges.append({"from": m["repo"], "to": dep})

    return (
        json.dumps(
            {
                "tiers": [
                    {"tier": t, "label": TIER_LABEL[t], "desc": TIER_DESC[t]}
                    for t in (3, 2, 1, 0)  # 渲染顺序：tier 3 在顶
                ],
                "nodes": nodes,
                "edges": edges,
                "dependents": {k: v for k, v in rev.items() if v},
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只校验，不写文件")
    args = ap.parse_args()

    data, mods = load()
    rev = reverse_deps(mods)
    import_root = data["importRoot"].format(org=data["defaultOrg"])

    expected = {}
    compat = compat_by_repo(data)
    for m in mods:
        expected[MODULES_OUT / f"{m['repo']}.md"] = render_module_page(
            m, rev, import_root, compat.get(m["repo"], [])
        )
    expected[MODULES_OUT / "index.md"] = render_modules_index(data, mods)
    expected[PARTS_OUT / "matrix-table.md"] = render_matrix_table(mods)
    expected[NAV_OUT] = (
        json.dumps(
            [{"repo": m["repo"], "tier": m["tier"]} for m in mods], indent=2, ensure_ascii=False
        )
        + "\n"
    )
    expected[GRAPH_OUT] = render_graph_data(data, mods, rev)

    stale = [
        p for p, content in expected.items()
        if not p.exists() or p.read_text(encoding="utf-8") != content
    ]

    if args.check:
        if stale:
            print("以下文件与 modules.json 不同步，请跑 npm run gen:modules：")
            for p in stale:
                print("  -", p.relative_to(ROOT))
            return 1
        print(f"OK：{len(expected)} 个生成文件均与 modules.json 同步")
        return 0

    for path, content in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print("wrote", path.relative_to(ROOT))

    print(f"\n共生成 {len(expected)} 个文件，{len(mods)} 个模块。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
