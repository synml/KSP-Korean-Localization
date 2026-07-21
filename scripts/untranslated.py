"""미번역(ko==en) 키를 분류해 나열한다 — 잔여 번역 작업의 작업 목록 생성기.

분류:
- keyword: 소문자 파트 검색 태그 라인 (번역 금지 — 인게임 파트 검색용 원문 태그)
- symbol:  25자 미만의 기호/단위/모델명 (n/a, m/s, Mk1-3, EC/s 등 — 원칙적으로 유지)
- todo:    실제 번역 후보 (장문 계약문·미션 문장·튜토리얼 등)

사용법:
    python scripts/untranslated.py                  # 분류별 개수 요약
    python scripts/untranslated.py --category todo  # 해당 분류의 "키<TAB>영문" 나열
    python scripts/untranslated.py --category todo --prefix 280  # 키 접두(#autoLOC_ 뒤) 필터

출력은 stdout. Windows 콘솔에서는 PYTHONIOENCODING=utf-8 필요.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter

from ksploc import FILE_PAIRS, parse_dictionary

KEYWORD_RE = re.compile(r"[a-z0-9 ()?\\!*-]+")
SYMBOL_RE = re.compile(r"[A-Za-z0-9 /.%<>=^:+-]+")


def classify(value: str) -> str:
    if KEYWORD_RE.fullmatch(value):
        return "keyword"
    # "Unavailable" 같은 5자 이상 단독 영단어는 번역 후보 (짧으면 Tab·NA 등 기호로 본다).
    if re.fullmatch(r"[A-Za-z]+", value) and len(value) >= 5:
        return "todo"
    if len(value) < 25 and SYMBOL_RE.fullmatch(value):
        # "Resources Depleted" 같은 공백 있는 순수 영문구도 번역 후보로 승격.
        # 숫자·기호가 섞이면 단위/모델명/템플릿("Mk1-3", "m/s", "T <<1>>")로 본다.
        if " " in value and not re.search(r"[0-9<>/^%:+=-]", value):
            return "todo"
        return "symbol"
    return "todo"


def key_stem(key: str) -> str:
    """키에서 #autoLOC_/#autoLoc_ 접두를 뗀 숫자부."""
    return re.sub(r"^#autoL[Oo][Cc]_", "", key)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", choices=["keyword", "symbol", "todo"])
    parser.add_argument("--prefix", help="#autoLOC_ 뒤 키 접두 필터 (예: 280)")
    args = parser.parse_args()

    rows: list[tuple[str, str, str]] = []  # (분류, 키, 영문)
    for en_path, ko_path in FILE_PAIRS:
        en_map = parse_dictionary(en_path).mapping()
        for entry in parse_dictionary(ko_path).entries:
            en_value = en_map.get(entry.key)
            if en_value is None or entry.value != en_value:
                continue
            if not re.search(r"[A-Za-z]", en_value):
                continue
            rows.append((classify(en_value), entry.key, en_value))

    if args.category:
        for cat, key, en_value in rows:
            if cat != args.category:
                continue
            if args.prefix and not key_stem(key).startswith(args.prefix):
                continue
            print(f"{key}\t{en_value}")
    else:
        counts = Counter(cat for cat, _, _ in rows)
        for cat in ("keyword", "symbol", "todo"):
            print(f"{cat:8s} {counts.get(cat, 0):5d}")
        print(f"{'total':8s} {len(rows):5d}")
        prefix_counts = Counter(
            key_stem(key)[:3] for cat, key, _ in rows if cat == "todo"
        )
        print("\ntodo 키 접두(#autoLOC_ 뒤 3자리) 분포:")
        for prefix, count in prefix_counts.most_common():
            print(f"  {prefix}* {count:4d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
