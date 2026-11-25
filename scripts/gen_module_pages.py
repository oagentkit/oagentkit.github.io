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

REFERENCE_OUT = DOCS / "reference"
VERSIONS = DOCS / "public" / "versions.json"

ORG = "https://github.com/oagentkit"

TIER_LABEL = {
    0: "tier 0 · 基础层",
    1: "tier 1 · 能力层",
    2: "tier 2 · 集成层",
    3: "tier 3 · 编排层",
    4: "tier 4 · 编排判据层",
    5: "tier 5 · 装配层",
}

TIER_DESC = {
    0: "零仓内依赖或仅依赖同仓包",
    1: "依赖 tier 0",
    2: "依赖 tier 0/1 + 重第三方地板",
    3: "依赖 llm 等 tier 2 门面",
    4: "依赖 guardx/toolgate 等 tier 0~2，编排判据单源（ADR-0010）",
    5: "依赖 goagent-kernel + agent，只接线不另写判据",
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


LEDGER_KINDS = ("retired", "compat", "moved")


def check_ledger_kinds(data: dict) -> list[str]:
    """账本条目的 kind 是否都在渲染器认得的集合里。

    kind 决定**渲染分支**（已退役 / 过渡期兼容镜像 / 矩阵内迁移）。
    拼错的 kind 不会让任何门禁变红——它只会被当成「非 compat 即退役」**静默**渲出
    错误措辞（对外公开的假陈述）⇒ 所以在生成器里就判死：**宁可生成失败**。

    与 gen_llms_txt.py 里「读不到门面包数 ⇒ 宁可生成失败」同一条纪律：
    **判不了 ≠ 没问题**。
    """
    out = []
    for entry in data.get("retiringPackages") or []:
        k = entry.get("kind")
        if k not in LEDGER_KINDS:
            out.append(f"{entry.get('pkg', '?')}(kind={k!r})")
    return out


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

    # 账本（retiringPackages）里混着三种东西，必须分开渲染：
    #   kind == "compat" → 过渡期兼容镜像：**路径仍然可用**；
    #   kind == "moved"  → **矩阵内迁移**：能力仍在矩阵里，只是搬到了别的模块
    #                      （例：obs/langfuse → llm/obsx，读写同域）；
    #   其它             → 已退役的包（那条路径已经没了，且能力搬出了本矩阵）。
    # 兼容镜像排前面：扫索引的人先看到「还能用的路径」，再看到历史。
    #
    # ⚠️ 「moved」不能套用 retired 的措辞（「已从本矩阵移出」）——那是**假陈述**：
    #   能力并没有离开矩阵。与 compat/retired 混渲是同一类问题，按 kind 分支处理。
    ledger = data.get("retiringPackages") or []
    bad_kinds = check_ledger_kinds(data)
    if bad_kinds:
        raise SystemExit(
            f"❌ retiringPackages 里有渲染器认不出的 kind：{bad_kinds}"
            "——kind 是判据面（retired / compat / moved），认不出的 kind 会被静默当成"
            "「已退役」渲染出错误措辞。宁可生成失败。"
        )
    for cp in [e for e in ledger if e.get("kind") == "compat"]:
        lines.extend(render_compat_section(cp))
    for rp in [e for e in ledger if e.get("kind") != "compat"]:
        pkg = rp.get("pkg", "?")
        repl = rp.get("replacement")
        moved = rp.get("kind") == "moved"
        lines.append(f"## {'已迁移的包' if moved else '已退役的包'}：{pkg}")
        lines.append("")
        if repl:
            if moved:
                lines.append(
                    f"`{pkg}` 已从 `{rp.get('repo')}` 仓移出，迁往 `{repl}`"
                    "（**仍在矩阵内**——能力没有消失，只是搬到了同域的模块）。"
                    "**迁移是分阶段完成的**：承接方先具备能力、来源方才删路径，"
                    "两边必须一起落地，缺一不可。"
                )
            else:
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
            f"{'迁移' if moved else '退役'}完整时间线见 [`{timeline}` 模块页]"
            f"(/modules/{timeline}.html) 的「本仓硬规则」。"
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



def load_versions():
    """版本矩阵（机器可读）。

    缺文件 / 坏 JSON 直接非零退出而不是静默用空值：判据跑不起来却报绿
    是最贵的失效形态——事实页会照抄一份不存在的矩阵。
    """
    try:
        return json.loads(VERSIONS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(
            f"ERROR: 读不到 {VERSIONS.relative_to(ROOT)}——"
            "先同步 matrix-tools 的 versions.json（源先、副本后）",
            file=sys.stderr,
        )
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: {VERSIONS.relative_to(ROOT)} 不是合法 JSON：{e}", file=sys.stderr)
        sys.exit(1)


def reconcile(mods, versions):
    """两份机器事实对账：模块集合、包集合、计数必须逐项相等。

    为什么这道对账放在生成器里：事实页若在两份数据不一致时照抄其中一份，
    读者看到的「67 个包」可能是假的——而没有任何门禁会红。两份数据分别来自
    matrix-tools 的两个产物（modules.json / versions.json），它们的漂移是
    真实发生过的形态。
    """
    problems = []
    dmods = {m["repo"]: m for m in mods}
    vmods = {m["repo"]: m for m in versions.get("modules") or []}

    only_d = sorted(set(dmods) - set(vmods))
    only_v = sorted(set(vmods) - set(dmods))
    if only_d or only_v:
        problems.append(
            f"模块集合不一致：modules.json 独有 {only_d} / versions.json 独有 {only_v}"
        )

    for repo in sorted(set(dmods) & set(vmods)):
        dp = set(dmods[repo].get("packages") or [])
        vp = {p["pkg"] for p in (vmods[repo].get("packages") or [])}
        if dp != vp:
            problems.append(
                f"{repo} 的包集合不一致：modules.json 独有 {sorted(dp - vp)} / "
                f"versions.json 独有 {sorted(vp - dp)}"
            )

    total = sum(len(m.get("packages") or []) for m in mods)
    if versions.get("moduleCount") != len(mods):
        problems.append(
            f"模块计数不一致：versions.json 自述 {versions.get('moduleCount')} / "
            f"modules.json 实算 {len(mods)}"
        )
    if versions.get("packageCount") != total:
        problems.append(
            f"包计数不一致：versions.json 自述 {versions.get('packageCount')} / "
            f"modules.json 实算 {total}"
        )

    if problems:
        for p in problems:
            print("ERROR: " + p, file=sys.stderr)
        print(
            "两份机器事实对账失败——事实页照抄任何一份都会写出假陈述，故直接退出。",
            file=sys.stderr,
        )
        sys.exit(1)


def render_packages_facts(data, mods, versions):
    """机器事实页：模块 × 包 × 版本的机器可读投影。

    这一页的每个数字都来自机器可读源（modules.json / versions.json），
    页面本体是**生成物**——手改会在下次生成时消失（这正是它该有的性质：
    数字不会被手抄漂移）。
    """
    vmods = {m["repo"]: m for m in versions.get("modules") or []}
    total_pkgs = sum(len(m.get("packages") or []) for m in mods)
    tier_count = len(data.get("tiers") or {})

    lines = []
    lines.append("# 机器事实：模块 × 包 × 版本")
    lines.append("")
    lines.append(
        "这一页是**机器可读事实的人读投影**：模块数、包数、import 路径、"
        "旧单仓路径、最新版本全部来自 `data/modules.json` 与 "
        "`docs/public/versions.json`，由 `scripts/gen_module_pages.py` 生成——"
        "**手改会在下次生成时消失**。"
    )
    lines.append("")
    lines.append(
        "同一份事实的机器可读形态：[`versions.json`](/versions.json) 与 "
        "[`llms.txt`](/llms.txt)。"
    )
    lines.append("")

    lines.append("## 总计")
    lines.append("")
    lines.append("| 项 | 值 |")
    lines.append("| --- | --- |")
    lines.append(f"| 模块 | {len(mods)} |")
    lines.append(f"| 包 | {total_pkgs} |")
    lines.append(f"| 层 | {tier_count}（tier 0 – tier {max(m['tier'] for m in mods)}） |")
    lines.append(f"| 组织 | `{versions.get('org')}` |")
    lines.append("| 源 | `oagentkit/matrix-tools`（模块与版本两份产物分别生成后对账） |")
    lines.append("")

    lines.append("## 逐模块")
    lines.append("")
    lines.append("| 模块 | 层 | 包数 | 最新版 | 仓内依赖 | 第三方地板 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for m in mods:
        deps = deps_of(m)
        deps_cell = "、".join(f"`{d}`" for d in deps) if deps else "—"
        heavy = m.get("heavyDeps") or []
        heavy_cell = "、".join(f"`{d}`" for d in heavy) if heavy else "零"
        latest = (vmods.get(m["repo"]) or {}).get("latest") or "—"
        lines.append(
            f"| [`{m['repo']}`](/modules/{m['repo']}.html) "
            f"| <span class=\"matrix-tier\">tier {m['tier']}</span> "
            f"| {len(m['packages'])} "
            f"| `{latest}` "
            f"| <span class=\"matrix-tier\">{deps_cell}</span> "
            f"| <span class=\"matrix-tier\">{heavy_cell}</span> |"
        )
    lines.append("")

    lines.append("## 全包清单")
    lines.append("")
    lines.append(
        "「旧单仓路径」是单仓时代（`git.enjoye.top/enjoydream/agentkit`）的包位置，"
        "改写工具据此做纯前缀映射——消费方改 import 时只需要替换前缀。"
    )
    lines.append("")
    lines.append("| 模块 | 包 | import 路径 | 旧单仓路径 |")
    lines.append("| --- | --- | --- | --- |")
    for m in mods:
        vpacks = {p["pkg"]: p for p in (vmods.get(m["repo"]) or {}).get("packages") or []}
        for p in m["packages"]:
            meta = vpacks.get(p) or {}
            legacy = meta.get("fromLegacy") or "—"
            default_path = (
                "github.com/"
                + versions.get("org", "oagentkit")
                + "/"
                + m["repo"]
                + "/"
                + p
            )
            lines.append(
                f"| `{m['repo']}` | `{p}` "
                f"| `{meta.get('importPath', default_path)}` "
                f"| `{legacy}` |"
            )
    lines.append("")

    lines.append("## 装机")
    lines.append("")
    lines.append("```bash")
    lines.append(f"go get {data['importRoot'].format(org=data['defaultOrg'])}/textx@latest")
    lines.append("```")
    lines.append("")
    lines.append(
        "装**模块**（`github.com/oagentkit/<仓名>`），不要装**包路径**——"
        "包路径只是模块里的一个目录，单独装拿不到版本。"
    )
    lines.append("")

    lines.append("## 相关")
    lines.append("")
    lines.append("- [模块总览](/modules/)")
    lines.append("- [坑速查](/reference/pitfalls.html) —— 已退役的包、兼容壳期限、层地板")
    lines.append("- [架构总览](/guide/architecture.html)")
    lines.append("")
    return "\n".join(lines)


def render_pitfalls(data, mods, versions):
    """坑速查页：账本 + 层规则，全部由数据推导。

    「手改会消失」在这里是**特性**：坑条目是会变的（包退役、期限临近），
    手抄一份很快就是一句假陈述。生成物至少保证它与机器事实同步。
    """
    lines = []
    lines.append("# 坑速查")
    lines.append("")
    lines.append(
        "矩阵里最容易踩的几坑，全部由 `data/modules.json` 的账本与层规则推导，"
        "由 `scripts/gen_module_pages.py` 生成——**手改会在下次生成时消失**。"
    )
    lines.append("")

    retired = [e for e in (data.get("retiringPackages") or []) if e.get("kind") != "compat"]
    lines.append("## 1. 已退役的包：那条路径已经没了")
    lines.append("")
    lines.append(
        "import 一个已退役的包**不会降级、不会告警，直接编译失败**——"
        "因为那条路径上已经没有包了。"
    )
    lines.append("")
    if retired:
        lines.append("| 包 | 迁往 | 状态 |")
        lines.append("| --- | --- | --- |")
        for e in retired:
            repl = e.get("replacement") or e.get("canonicalPath") or "—"
            status = e.get("status") or e.get("action") or "—"
            lines.append(f"| `{e.get('pkg', '?')}` | `{repl}` | {status} |")
        lines.append("")
        for e in retired:
            if e.get("consumedBy"):
                lines.append(f"- `{e.get('pkg')}` —— 消费方：{e['consumedBy']}")
            if e.get("issueChain"):
                lines.append(f"- `{e.get('pkg')}` —— 需求链：")
                lines.extend(issue_links(e))
            lines.append("")
    else:
        lines.append("（当前账本里没有已退役的包条目。）")
        lines.append("")

    compat = [e for e in (data.get("retiringPackages") or []) if e.get("kind") == "compat"]
    shells = data.get("compatShells") or []
    lines.append("## 2. 兼容镜像与兼容壳：路径还在，但有期限")
    lines.append("")
    lines.append(
        "兼容层是**有保质期**的：到期后上游删掉它，依赖它的代码在**升级上游之后**"
        "才编译失败——本地还绿、CI 才红，是最难查的一类断。"
    )
    lines.append("")
    if compat:
        lines.append("| 包 | 规范路径 | 起始版本 | 状态 |")
        lines.append("| --- | --- | --- | --- |")
        for e in compat:
            lines.append(
                f"| `{e.get('pkg', '?')}` | `{e.get('canonicalPath', '—')}` "
                f"| {e.get('availableIn', '—')} | {e.get('status', '—')} |"
            )
        lines.append("")
    if shells:
        lines.append("| 仓 | 壳路径 | 旧 import 路径 | 兼容至 | 已删除于 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for s in shells:
            lines.append(
                f"| `{s.get('repo')}` | `{s.get('path')}` | `{s.get('module')}` "
                f"| `{s.get('until')}` | `{s.get('removedIn')}` |"
            )
        lines.append("")
    if not compat and not shells:
        lines.append("（当前没有登记在册的兼容镜像 / 兼容壳。）")
        lines.append("")

    facades = [r for r in (data.get("infraRepos") or []) if r.get("retired")]
    lines.append("## 3. 门面仓已退役：转发层不再转发")
    lines.append("")
    if facades:
        for fr in facades:
            ret = fr.get("retired") or {}
            lines.append(
                f"`{fr['repo']}` 是门面仓（re-export 兼容层），"
                f"**{ret.get('version', '—')} 起已退役**"
                f"（{ret.get('date', '—')}）："
                f"{ret.get('packagesDeleted', '—')} 个转发包全部删除，"
                f"旧 import 路径 `{versions.get('org', 'oagentkit')}/{fr['repo']}/*` 一律编译失败。"
            )
            lines.append("")
            if ret.get("reason"):
                lines.append(f"- 退役原因：{ret['reason']}")
            if ret.get("decidedBy"):
                lines.append(f"- 决策：{ret['decidedBy']}")
            lines.append("")
    else:
        lines.append("（当前没有已退役的门面仓。）")
        lines.append("")

    lines.append("## 4. 层地板：tier 0 / tier 1 不得有重量级第三方依赖")
    lines.append("")
    lines.append(
        "tier 由**依赖地板**决定，不是由功能多少决定。tier 0 / tier 1 必须零重量级"
        "第三方依赖——所以它们能被任何下游安全依赖；一旦某个 tier 0 仓引了 eino 或"
        "数据库驱动，它就不再是 tier 0，整条依赖链的地基都跟着变重。"
    )
    lines.append("")
    lines.append("| 模块 | 层 | 重量级第三方依赖 |")
    lines.append("| --- | --- | --- |")
    for m in mods:
        heavy = m.get("heavyDeps") or []
        heavy_cell = "、".join(f"`{d}`" for d in heavy) if heavy else "零"
        lines.append(
            f"| [`{m['repo']}`](/modules/{m['repo']}.html) "
            f"| <span class=\"matrix-tier\">tier {m['tier']}</span> "
            f"| <span class=\"matrix-tier\">{heavy_cell}</span> |"
        )
    lines.append("")
    lines.append(
        "判据脚本：`matrix-tools/scripts/verify_dep_floor.py`——"
        "它读的是 `heavyDeps` 登记，不是读 go.mod 猜。"
    )
    lines.append("")

    lines.append("## 5. 依赖方向：tier N 不得依赖 tier > N")
    lines.append("")
    lines.append(
        "依赖严格自底向上。**反向依赖（tier 0 依赖 tier 3）不是「暂时方便」，"
        "是分层失效**——它让「上层坐在下层之上」的读法不再成立，"
        "依赖图也就没法用层号排序了。"
    )
    lines.append("")
    lines.append("| 模块 | 层 | 仓内依赖 |")
    lines.append("| --- | --- | --- |")
    tier_of = {m["repo"]: m["tier"] for m in mods}
    for m in mods:
        deps = deps_of(m)
        dep_cells = []
        for d in deps:
            dt = tier_of.get(d)
            dep_cells.append(f"`{d}`" + (f"（tier {dt}）" if dt is not None else ""))
        lines.append(
            f"| [`{m['repo']}`](/modules/{m['repo']}.html) "
            f"| <span class=\"matrix-tier\">tier {m['tier']}</span> "
            f"| <span class=\"matrix-tier\">{'、'.join(dep_cells) if dep_cells else '—'}</span> |"
        )
    lines.append("")
    lines.append(
        "判据脚本：`matrix-tools/scripts/verify_import_direction.py`"
        "（层级方向 + 依赖声明对账）。"
    )
    lines.append("")

    lines.append("## 相关")
    lines.append("")
    lines.append("- [机器事实](/reference/packages.html) —— 模块 × 包 × 版本")
    lines.append("- [模块总览](/modules/)")
    lines.append("- [架构总览](/guide/architecture.html)")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只校验，不写文件")
    args = ap.parse_args()

    data, mods = load()
    rev = reverse_deps(mods)
    import_root = data["importRoot"].format(org=data["defaultOrg"])
    versions = load_versions()
    # 两份机器事实先对账再渲染：事实页照抄任何一份都会写出假陈述
    reconcile(mods, versions)

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
    expected[REFERENCE_OUT / "packages.md"] = render_packages_facts(data, mods, versions)
    expected[REFERENCE_OUT / "pitfalls.md"] = render_pitfalls(data, mods, versions)

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
