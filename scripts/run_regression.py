#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_regression.py — 提示词检查回归对比（video-prompt-optimizer 配套）

用途：改完 skill / 改了 lint 规则后，一键重跑全部测试用例，与 baseline.json 对比，
      打印每条用例 ↑/↓/持平 及总分变化，立刻发现"是不是改坏了"。

工作流：
  1. 首次建立基线：  python run_regression.py --update-baseline
  2. 之后每次改动后：python run_regression.py
  3. 只看结果：      python run_regression.py --quiet

退出码：0 = 无回归（没有 fail 变多 / 分数没掉）；1 = 检测到回归。
"""

import os
import sys
import json
import glob
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
CASES_DIR = os.path.join(SKILL_ROOT, "tests", "cases")
BASELINE = os.path.join(SKILL_ROOT, "tests", "baseline.json")
LINT = os.path.join(HERE, "lint_prompt.py")


def lint_one(path):
    """调用 lint_prompt.py --json，返回 {score, all_pass, fails}"""
    out = subprocess.run(
        [sys.executable, LINT, path, "--json"],
        capture_output=True, text=True, encoding="utf-8"
    )
    try:
        d = json.loads(out.stdout)
    except json.JSONDecodeError:
        return {"score": 0.0, "all_pass": False, "fails": ["PARSE_ERROR"]}
    fails = [r["id"] for r in d["results"] if not r["ok"]]
    return {"score": d["score"], "all_pass": d["all_pass"], "fails": fails}


def collect():
    result = {}
    for path in sorted(glob.glob(os.path.join(CASES_DIR, "*.txt"))):
        name = os.path.basename(path)
        result[name] = lint_one(path)
    return result


def load_baseline():
    if not os.path.exists(BASELINE):
        return None
    with open(BASELINE, "r", encoding="utf-8") as f:
        return json.load(f)


def update_baseline(current):
    data = {"cases": current}
    with open(BASELINE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 基线已更新 → {BASELINE}")
    print(f"   共 {len(current)} 条用例")
    for name, r in current.items():
        print(f"   - {name}: {r['score']}%  {'PASS' if r['all_pass'] else 'FAIL ' + str(r['fails'])}")


def compare(current, base):
    base_cases = base.get("cases", {})
    regressions = []
    improvements = []
    rows = []

    all_names = sorted(set(list(current.keys()) + list(base_cases.keys())))
    for name in all_names:
        cur = current.get(name)
        old = base_cases.get(name)
        if cur is None:
            rows.append((name, "REMOVED", "-", "-", "⚠️ 用例被删"))
            continue
        if old is None:
            rows.append((name, "NEW", "-", f"{cur['score']}%", "🆕 新增"))
            continue
        delta = cur["score"] - old["score"]
        old_fails = set(old.get("fails", []))
        new_fails = set(cur.get("fails", []))
        added_fails = new_fails - old_fails
        if delta < 0 or added_fails:
            regressions.append(name)
            tag = f"❌ 回归 {delta:+.1f}%  新增失败:{sorted(added_fails)}"
        elif delta > 0 or (old_fails - new_fails):
            improvements.append(name)
            tag = f"✅ 改善 {delta:+.1f}%"
        else:
            tag = "持平"
        rows.append((name, f"{old['score']}%", f"{cur['score']}%", f"{delta:+.1f}%", tag))

    # 打印表
    print(f"\n=== 回归对比  |  基线 {len(base_cases)} 条 vs 当前 {len(current)} 条 ===\n")
    print(f"{'用例':<28}{'基线':>8}{'当前':>8}{'变化':>9}  状态")
    print("-" * 72)
    for name, old_s, cur_s, delta, tag in rows:
        print(f"{name:<28}{old_s:>8}{cur_s:>8}{delta:>9}  {tag}")

    print()
    if regressions:
        print(f"❌ 检测到 {len(regressions)} 处回归: {regressions}")
        return False
    if improvements:
        print(f"✅ 无回归，且有 {len(improvements)} 处改善: {improvements}")
        print("   如确认改善符合预期，可运行 --update-baseline 固化新基线。")
    else:
        print("✅ 无变化，无回归。")
    return True


def main():
    quiet = "--quiet" in sys.argv
    update = "--update-baseline" in sys.argv

    current = collect()
    if not current:
        print(f"❌ 没有找到用例（{CASES_DIR}/*.txt）")
        sys.exit(1)

    if update:
        update_baseline(current)
        sys.exit(0)

    base = load_baseline()
    if base is None:
        print("⚠️ 基线不存在。先运行：python run_regression.py --update-baseline")
        print("   当前结果：")
        for name, r in current.items():
            print(f"   - {name}: {r['score']}%  {'PASS' if r['all_pass'] else 'FAIL'}")
        sys.exit(1)

    ok = compare(current, base)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
