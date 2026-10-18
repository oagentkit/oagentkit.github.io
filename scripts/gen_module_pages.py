#!/usr/bin/env python3
"""
由 data/modules.json 生成 oagentkit 文档站的模块页、侧边栏与首页矩阵表。

单一数据源：data/modules.json（从 matrix-tools 仓同步而来，schema 同源）。
仓间依赖（INTRA_DEPS）不在 modules.json 里 —— 它只记录第三方依赖地板 ——
所以这里显式维护一份，并在 CI/提交时人工核对与 llms.txt 一致。

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

# 仓间依赖（intra-matrix）。modules.json 不含此项，此表须与 llms.txt 的
# 「依赖：」行保持一致 —— 改这里就同步改 llms.txt。
INTRA_DEPS = {
    "textx": [],
    "runtime": [],
    "guardx": [],
    "queue": [],
    "promptx": ["runtime", "textx"],
    "obs": ["textx"],
    "skillkit": ["guardx", "textx"],
    "mcpkit": ["runtime"],
    "rag": ["textx"],
    "llm": ["obs", "runtime", "textx"],
    "toolgate": ["mcpkit"],
    "tools": ["guardx", "runtime", "textx"],
    "agent": ["llm", "textx"],
}


def load():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    mods = sorted(data["modules"], key=lambda m: (m["tier"], m["repo"]))
    return data, mods


def reverse_deps(mods):
    """repo -> 直接依赖它的仓列表。"""
    rev = {m["repo"]: [] for m in mods}
    for m in mods:
        for dep in INTRA_DEPS.get(m["repo"], []):
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
        deps = INTRA_DEPS.get(m["repo"], [])
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
    deps = INTRA_DEPS.get(repo, [])
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
            deps = INTRA_DEPS.get(m["repo"], [])
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
