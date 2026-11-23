#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lint_prompt.py — 提示词「客观硬伤」扫描器（video-prompt-optimizer 配套）

定位（2026-10-27 架构修正后）：
  本脚本只做**机械断言**——检查"客观属性在不在"，不做任何**语义判断**。
  语义判断（这个词在这个语境里是不是模糊/是不是审核雷区/方位有没有锚）
  一律交给**执行 skill 的 LLM**按 references 文档（word-judgment.md / audit-avoidance.md）去判——
  LLM 理解语义，不需要靠词表+豁免清单硬凑，那条路注定要无穷补豁免、且永远误伤。

  ┌─ 机械断言（本脚本做）：有没有否定句、运镜是不是同时写了两种、必补维度缺没缺、守卫词超不超量
  └─ 语义判断（LLM 做，不在本脚本）：模糊词/审核雷区/方位锚定——见 SKILL.md 第 1/4 步

  → 所以 lint 的分数只反映"结构硬伤"，不反映"用词好不好"。用词好不好由 LLM 按文档判 + 渲染抽检。

设计原则：
  - 纯 Python 标准库，无第三方依赖、无网络。
  - 只断言"无歧义的客观属性"；凡是需要理解语义才能判的，不进本脚本。
  - 通过率分数用于回归对比（run_regression.py 调它），不是绝对的"好坏分"。

用法：
  python lint_prompt.py 提示词.txt
  python lint_prompt.py -            # 从 stdin 读
  echo "提示词…" | python lint_prompt.py -
  python lint_prompt.py 提示词.txt --json    # 输出机器可读 JSON（供回归脚本调用）

退出码：0 = 全部通过；1 = 有 fail（便于 CI / 批量脚本判断）
"""

import sys
import json
import argparse

# ============ 规则定义（只保留机械断言）============
# 每条规则：id / 描述 / 权重 / 检查函数(text)->(ok:bool, detail:str)
# ok=True 表示通过。权重用于计算加权通过率。

# —— 负向句式：正文不该出现"不要/没有/别"开头的否定（skill 硬约束 11）——
# 机械：查字符串里有没有这些否定模板。无歧义。
NEG_PATTERNS = ["不要", "没有出现", "别出现", "不能出现", "禁止"]

# —— 剪辑台指令：BGM/配乐/定格/闪白/转场（skill 硬约束 7、9）——
# 机械：这些是明确的剪辑台术语，出现即违规（文生视频不该带剪辑指令）。
EDIT_TERMS = ["BGM", "bgm", "配乐", "背景音乐", "画面定格", "镜头定格",
              "闪白", "转场", "配乐高潮", "戛然而止", "淡入", "淡出",
              "镜头切换", "蒙太奇"]

# —— 必补维度存在性检查：景别 / 运镜 / 光线来源 / 色调 ——
# 机械：查"这个维度的词有没有写"，不判"写得对不对"（那是语义，归 LLM）。
SHOT_SIZE = ["大远景", "全景", "中景", "中近景", "近景", "特写", "大特写"]
CAMERA_MOVE = ["固定机位", "固定", "缓推", "推近", "缓拉", "拉远", "平移",
               "横向平移", "跟随", "跟摇", "上摇", "手持", "摇镜", "推镜",
               "前推", "推进", "向前推", "后拉", "横移", "跟拍"]
LIGHT_SOURCE_HINT = ["窗", "灯", "火", "月", "光柱", "阳光", "月光", "霓虹",
                     "烛", "屏幕光", "反光", "逆光", "侧光", "顶光", "底光",
                     "光源", "光从", "照亮", "照来", "打来",
                     # 光质 + 方向 + 光线动作（合法光线描述，无需具名光源物件）
                     "硬光", "软光", "顶部", "侧面光", "直射", "斜射", "斜照",
                     "打下", "打在", "洒下", "洒在", "透下", "透进", "勾出", "勾勒"]
TONE_WORDS = ["色调", "冷蓝", "暖黄", "暖褐", "墨黑", "黑白", "低饱和", "高饱和",
              "冷暖对比", "青橙", "冷调", "暖调", "冷紫", "紫金", "紫蓝", "赤红",
              "橘红", "灰白", "灰调", "单色", "色温", "中性色"]

# —— 守卫词（正向护栏，2-4 条封顶）——
# 机械：数护栏词条数，超量即稀释。无歧义。
GUARD_WORDS = ["画面锐利清晰", "结构正常", "结构稳定", "不变形", "固定机位画面稳定",
               "画面稳定流畅", "画面干净", "无文字", "无文字元素"]


def _find(text, terms):
    return [t for t in terms if t in text]


def check_negative(text):
    hits = _find(text, NEG_PATTERNS)
    return (len(hits) == 0, f"命中负向句式:{hits}" if hits else "无负向句式")


def check_edit_terms(text):
    hits = _find(text, EDIT_TERMS)
    return (len(hits) == 0, f"命中剪辑台指令:{hits}" if hits else "无剪辑台指令")


def check_shot_size(text):
    hits = _find(text, SHOT_SIZE)
    return (len(hits) > 0, f"景别:{hits}" if hits else "缺景别（必补）")


def check_camera_move(text):
    hits = _find(text, CAMERA_MOVE)
    # 去掉重复（"固定机位"和"固定"重复算一个）
    uniq = set()
    for h in hits:
        if h in ("固定", "固定机位"):
            uniq.add("固定")
        elif h in ("推近", "缓推", "推镜", "前推", "推进", "向前推"):
            uniq.add("推")
        elif h in ("拉远", "缓拉", "后拉"):
            uniq.add("拉")
        elif h in ("平移", "横向平移", "横移"):
            uniq.add("平移")
        elif h in ("跟随", "跟摇", "跟拍"):
            uniq.add("跟")
        else:
            uniq.add(h)
    if not hits:
        return (False, "缺运镜（必补）")
    if len(uniq) > 1:
        return (False, f"运镜不单一（应只用一种）:{sorted(uniq)}")
    return (True, f"运镜单一:{sorted(uniq)}")


def check_light(text):
    hits = _find(text, LIGHT_SOURCE_HINT)
    return (len(hits) > 0, f"光线来源:{hits[:4]}" if hits else "缺光线来源（必补）")


def check_tone(text):
    hits = _find(text, TONE_WORDS)
    return (len(hits) > 0, f"色调:{hits[:3]}" if hits else "缺色调（必补）")


def check_guard(text):
    # 按出现位置做区间合并，避免连写的护栏词（"画面干净无文字"）被重复计数
    spans = []
    for w in GUARD_WORDS:
        start = text.find(w)
        while start != -1:
            spans.append((start, start + len(w)))
            start = text.find(w, start + 1)
    if not spans:
        return (True, "无守卫词（可选，建议2-4条）")
    spans.sort()
    merged = 1
    cur_end = spans[0][1]
    for s, e in spans[1:]:
        if s <= cur_end:  # 重叠或相邻，算同一条护栏
            cur_end = max(cur_end, e)
        else:
            merged += 1
            cur_end = e
    if merged > 4:
        return (False, f"守卫词过多({merged}条)，应≤4条防稀释")
    return (True, f"守卫词{merged}条(≤4)")


# RULES = 只保留机械断言。
# 【已移除的语义规则，交回 LLM 判，别再加回脚本】：
#   - VAGUE_VERB  模糊词检测  → LLM 按 word-judgment.md 四象限判"够不够具体"
#   - AUDIT       审核敏感词  → LLM 按 audit-avoidance.md 雷区自查
#   - REL_POS     方位锚定    → LLM 自检"方位词前有没有机位/画面坐标"
#   移除原因：这三条要理解语义才判得准，用词表+豁免硬匹配注定无穷补豁免且持续误伤
#   （打光的打/仿佛的佛/做旧的做/画面锐利清晰的画面都曾被误伤）。LLM 天然懂语义，不需要词表。
RULES = [
    ("NEG_NEGATION", "正文无否定句式", 2, check_negative),
    ("EDIT_TERMS", "无剪辑台指令", 2, check_edit_terms),
    ("SHOT_SIZE", "景别（必补）", 1, check_shot_size),
    ("CAMERA_MOVE", "运镜单一（必补）", 2, check_camera_move),
    ("LIGHT", "光线来源（必补）", 1, check_light),
    ("TONE", "色调（必补）", 1, check_tone),
    ("GUARD", "守卫词不超量", 1, check_guard),
]


def lint(text):
    """返回 (score: float 0-100, results: list of dict, passed: bool)"""
    results = []
    total_w = 0
    got_w = 0
    for rid, desc, weight, fn in RULES:
        ok, detail = fn(text)
        results.append({"id": rid, "desc": desc, "ok": ok, "weight": weight, "detail": detail})
        total_w += weight
        if ok:
            got_w += weight
    score = round(got_w / total_w * 100, 1) if total_w else 0.0
    all_pass = all(r["ok"] for r in results)
    return score, results, all_pass


def read_input(arg):
    if arg == "-":
        return sys.stdin.read()
    with open(arg, "r", encoding="utf-8") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser(description="提示词客观硬伤扫描器（只做机械断言，语义判断归 LLM）")
    ap.add_argument("source", help="提示词文件路径，或 '-' 表示从 stdin 读")
    ap.add_argument("--json", action="store_true", help="输出机器可读 JSON（供回归脚本用）")
    args = ap.parse_args()

    text = read_input(args.source)
    score, results, all_pass = lint(text)

    if args.json:
        print(json.dumps({"score": score, "all_pass": all_pass, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        print(f"=== 提示词硬伤扫描  |  通过率 {score}%  |  {'✅ 全通过' if all_pass else '❌ 有未通过项'} ===")
        print("   （只查结构硬伤；用词是否模糊/踩审核雷区，由 LLM 按 word-judgment / audit-avoidance 判）\n")
        for r in results:
            mark = "✅" if r["ok"] else "❌"
            print(f" {mark} [{r['id']}] {r['desc']}  (w={r['weight']})")
            print(f"      {r['detail']}")
        print()

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
