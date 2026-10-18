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


def render_module_page(m, rev, import_root):
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

    for rp in data.get("retiringPackages") or []:
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
            for num, desc in chain.items():
                lines.append(f"  - [`#{num}`](https://github.com/oekit/concurrency/issues/{num}) —— {desc}")
        if rp.get("action"):
            lines.append(f"- 后续：{rp['action']}")
        lines.append("")
        lines.append(
            "退役完整时间线见 [`runtime` 模块页](/modules/runtime.html) 的「本仓硬规则」。"
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
    for m in mods:
        expected[MODULES_OUT / f"{m['repo']}.md"] = render_module_page(m, rev, import_root)
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
