"""reference_english/ 원문 ↔ GameData의 ko 사전 정합성 검증.

검사 항목 (CLAUDE.md '검증 자동화' 절):
1. 키 집합 일치 (누락/잉여/중복 키)
2. Lingoona 변수 태그(<<1>>, <<A:1>> 등) 집합 일치 — 위치 이동은 허용, 추가/삭제/변형은 오류
3. 리치 텍스트 태그(<b>, <color=...> 등) 짝 맞춤 + 원문 대비 개수 비교
4. 값 안의 { } // 검출 (cfg 파서가 오동작하거나 값이 잘리는 원인)
5. cfg 문법 파싱 (중괄호 균형 — 파서가 겸함)
6. 값 안의 리터럴 \n 개수 비교 (경고)
7. 한국어 맞춤법·용어 (ko 값 자체): 용어 이형·확정 오타·의존명사 띄어쓰기.
   '항상 틀린' 형태만 오류로 잡는다 — SPELL_BANNED / korean_spelling_issues 참고,
   예외는 SPELLING_WAIVERS에 근거와 함께 등록.

종료 코드 0 = 오류 없음(커밋 가능), 1 = 오류 있음. --strict는 경고도 실패로 취급.

사용법: python scripts/validate.py [--strict] [--verbose]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

# cp949 등 비UTF-8 콘솔에서 요약 줄의 em-dash(—) 등이 UnicodeEncodeError로 크래시하는 것 방지
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ksploc import FILE_PAIRS, REPO_ROOT, parse_dictionary

LINGOONA_RE = re.compile(r"<<[^<>]*>>")
LINGOONA_ARG_RE = re.compile(r"\d+")
RICH_TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)(?:=[^<>]*)?\s*>")

# ── 한국어 맞춤법·용어 검사 (ko 값 자체만 봄. 원문 대조 아님) ──────────────
# 편입 경위: 매 전수 검토 때마다 임시 스크립트로 잡던 '규칙으로 잡히는' 오류를
# 상시 게이트로 승격해 재발을 막는다. 여기 등록된 것은 전부 '항상 틀린' 형태이며,
# 현재 코퍼스에서 0건임을 확인하고 오류로 넣었다 (오탐이 커밋을 막지 않도록).

# 항상-틀린 문자열 → (분류, 올바른 형태). 부분 문자열 포함 검사.
SPELL_BANNED: dict[str, tuple[str, str]] = {
    # 용어 이형 (docs/glossary.md 표준)
    "워프": ("용어 이형", "시간 가속"),
    "매뉴버": ("용어 이형", "메뉴버"),
    "쓰로틀": ("용어 이형", "스로틀"),
    "케르맨": ("용어 이형", "커맨"),
    "케르발": ("용어 이형", "커벌"),
    "라디에이터": ("용어 이형", "방열기"),
    "웨이포인트": ("용어 이형", "경유지"),
    "아포압시스": ("용어 이형", "최원점"),
    "페리압시스": ("용어 이형", "최근점"),
    "플라이바이": ("용어 이형", "근접 통과"),
    "네비볼": ("용어 이형", "항법구"),
    "네브볼": ("용어 이형", "항법구"),
    "데스티네이션": ("용어 이형", "목표"),
    "모노프로펠런트": ("용어 이형", "단일추진제"),
    "클라이드데일": ("용어 이형", "클라이즈데일"),
    "썸퍼": ("용어 이형", "섬퍼"),
    # Delta-v 음차·이형 → 표준 Δv (델타익·델타타임 등은 토큰이 달라 무충돌)
    "델타-v": ("용어 이형", "Δv"),
    "델타V": ("용어 이형", "Δv"),
    "델타v": ("용어 이형", "Δv"),
    "deltaV": ("용어 이형", "Δv"),
    # 확정 오타·맞춤법
    "되서": ("맞춤법", "돼서"),
    "됬": ("맞춤법", "됐"),
    "되요": ("맞춤법", "돼요"),
    "안돼": ("맞춤법(띄어쓰기)", "안 돼"),
    "몇일": ("맞춤법", "며칠"),
    "왠만": ("맞춤법", "웬만"),
    "웬지": ("맞춤법", "왠지"),
    "할려고": ("맞춤법", "하려고"),
    "볼려고": ("맞춤법", "보려고"),
    "갈려고": ("맞춤법", "가려고"),
    "어떻해": ("맞춤법", "어떡해/어떻게 해"),
    "오랫만": ("맞춤법", "오랜만"),
    "금새": ("맞춤법", "금세"),
}

# 의존명사 '수/때/것' 앞에서 종성 ㄹ을 붙여 쓴 오류를 잡되, 아래는 붙여쓰는 게 맞아 제외.
_RIEUL = 8  # 종성 인덱스 ㄹ
_DEP_NOUNS = frozenset("수때것")
# 붙여쓰는 게 맞는 한자어/합성어 2-gram (오탐 방지 allowlist)
_DEP_NOUN_ALLOW = frozenset(
    {
        "필수",
        "실수",
        "골수",
        "밀수",
        "정수",
        "일수",
        "회수",
        "강수",
        "방수",
        "홀수",
        "촉수",
        "액수",
        "결수",
        "별수",
        "술수",
        "절수",
        "물수",
        "설수",
        "급수",
        "감수",
        "상수",
        "변수",
        "함수",
        "제수",
        "인수",
        "물때",
        "날것",
        "들것",
        "탈것",
        "별것",
        "생것",
    }
)


def _final_jamo(ch: str) -> int:
    return (ord(ch) - 0xAC00) % 28 if "가" <= ch <= "힣" else -1


def korean_spelling_issues(value: str) -> list[tuple[str, str]]:
    """(분류, 근거 조각) 목록. 비어 있으면 문제 없음."""
    issues: list[tuple[str, str]] = []
    for bad, (category, good) in SPELL_BANNED.items():
        if bad in value:
            issues.append((category, f"{bad!r} → {good!r}"))
    # 의존명사 띄어쓰기
    for i in range(1, len(value)):
        c = value[i]
        if c in _DEP_NOUNS and _final_jamo(value[i - 1]) == _RIEUL:
            if c == "수" and value[i + 1 : i + 2] == "록":
                continue  # -ㄹ수록 연결어미
            if value[i - 1 : i + 1] in _DEP_NOUN_ALLOW:
                continue
            issues.append(
                ("의존명사 띄어쓰기", f"...{value[max(0, i - 4) : i + 2]}...")
            )
    # '때문'은 체언/관형형 뒤에서 항상 띄어 쓴다. '텐데'(터+ㄴ데)도 관형형 뒤 띄어 씀
    # ('X텐데'로 붙는 다른 한국어 낱말은 없음 → 앞이 한글이면 항상 오류).
    for word in ("때문", "텐데"):
        start = 0
        while (j := value.find(word, start)) >= 0:
            prev = value[j - 1] if j > 0 else " "
            if prev != " " and "가" <= prev <= "힣":
                issues.append(
                    ("의존명사 띄어쓰기", f"...{value[max(0, j - 4) : j + 2]}...")
                )
            start = j + 2
    return issues


# 의도적으로 원문과 태그가 다른 키. 값 = 근거. 남발 금지 — 새 항목은 근거 필수.
LINGOONA_WAIVERS = {
    # en: "Ferry <<n:1[...]>> ... to <<o:2>> <<n:3[destination/...]>>".
    # o:2(목적지 개수)는 한국어 문장에서 생략. 우크라이나 패치도 동일하게 생략한 선례 있음.
    "#autoLOC_7000003": "o:2 목적지 개수 생략 (uk 패치 동일)",
}

# 한국어 맞춤법 검사(korean_spelling_issues)를 건너뛸 키. 의도적으로 규칙에 어긋나는
# 값(깨진 통신문 등)만 근거와 함께 등록. 남발 금지.
SPELLING_WAIVERS: dict[str, str] = {
    "#autoLOC_501435": "의도적으로 깨진 통신문 (자모·기호 노출이 원문 대응)",
}

# TMP에서 여는/닫는 짝이 필요한 태그. 이 외(sprite, pos 등)는 단독 사용 가능.
PAIRED_TAGS = {
    "b",
    "i",
    "u",
    "s",
    "color",
    "size",
    "style",
    "font",
    "material",
    "mark",
    "sub",
    "sup",
    "noparse",
    "nobr",
    "link",
    "voffset",
    "cspace",
    "lowercase",
    "uppercase",
    "smallcaps",
    "align",
}


def lingoona_info(value: str) -> tuple[set[int], Counter]:
    """(참조하는 인자 번호 집합, 태그 시그니처 멀티셋).

    대괄호 안 복수형/성별 형태는 번역 대상이므로 시그니처에서는 형태 개수만 남긴다.
    예: <<n:1[ part/ part/ parts]>> → 'n:1[3]', <<A:1>> → 'A:1', <<2>> → '2'
    """
    args: set[int] = set()
    signatures: Counter = Counter()
    for tag in LINGOONA_RE.findall(value):
        content = tag[2:-2]
        prefix, bracket, forms = content.partition("[")
        args.update(int(n) for n in LINGOONA_ARG_RE.findall(prefix))
        if bracket:
            signatures[f"{prefix}[{forms.count('/') + 1}]"] += 1
        else:
            signatures[prefix] += 1
    return args, signatures


def rich_tag_counts(value: str) -> Counter:
    """태그 이름별 (이름, 여는/닫는) 개수. Lingoona 태그는 먼저 제거하고 센다."""
    stripped = LINGOONA_RE.sub("", value)
    counts: Counter = Counter()
    for close, name in (
        (m.group(1), m.group(2).lower()) for m in RICH_TAG_RE.finditer(stripped)
    ):
        counts[(name, "close" if close else "open")] += 1
    return counts


def paired_tags_balanced(counts: Counter) -> bool:
    return all(
        counts[(name, "open")] == counts[(name, "close")]
        for name in PAIRED_TAGS
        if counts[(name, "open")] or counts[(name, "close")]
    )


class Report:
    def __init__(self, name: str, verbose: bool) -> None:
        self.name = name
        self.verbose = verbose
        self.errors: dict[str, list[str]] = {}
        self.warnings: dict[str, list[str]] = {}

    def error(self, category: str, message: str) -> None:
        self.errors.setdefault(category, []).append(message)

    def warning(self, category: str, message: str) -> None:
        self.warnings.setdefault(category, []).append(message)

    def print(self) -> None:
        for label, groups in (("오류", self.errors), ("경고", self.warnings)):
            for category, messages in groups.items():
                limit = len(messages) if self.verbose else 30
                for message in messages[:limit]:
                    print(f"  [{label}] {category}: {message}")
                if len(messages) > limit:
                    print(f"  [{label}] {category}: ... 외 {len(messages) - limit}건")

    @property
    def error_count(self) -> int:
        return sum(len(v) for v in self.errors.values())

    @property
    def warning_count(self) -> int:
        return sum(len(v) for v in self.warnings.values())


def validate_pair(english_path, ko_path, verbose: bool) -> Report:
    report = Report(ko_path.name, verbose)
    english = parse_dictionary(english_path)
    ko = parse_dictionary(ko_path)

    if ko.language != "ko":
        report.error("언어 노드", f"노드 이름이 {ko.language!r} (기대값 'ko')")

    for key, n in ko.duplicates().items():
        report.error("중복 키", f"{key} ({n}회)")

    en_map = english.mapping()
    ko_map = ko.mapping()
    for key in en_map:
        if key not in ko_map:
            report.error("키 누락", key)
    for key in ko_map:
        if key not in en_map:
            report.error("잉여 키", key)

    for entry in ko.entries:
        if entry.comment is not None:
            report.error(
                "값 내 //", f"{entry.key}:{entry.line_no} — // 이후가 게임에서 잘림"
            )

    for key, ko_value in ko_map.items():
        if key in SPELLING_WAIVERS:
            continue
        for category, evidence in korean_spelling_issues(ko_value):
            report.error(f"한국어 {category}", f"{key}: {evidence}")

    for key, en_value in en_map.items():
        ko_value = ko_map.get(key)
        if ko_value is None:
            continue

        if not ko_value and en_value:
            report.error("빈 값", key)
            continue

        if "{" in ko_value or "}" in ko_value:
            if "{" not in en_value and "}" not in en_value:
                report.error("값 내 중괄호", f"{key}: {ko_value[:60]!r}")

        en_args, en_sigs = lingoona_info(en_value)
        ko_args, ko_sigs = lingoona_info(ko_value)
        if en_args - ko_args:
            if key in LINGOONA_WAIVERS:
                report.warning(
                    "Lingoona 변수 누락(예외 승인됨)",
                    f"{key}: {LINGOONA_WAIVERS[key]}",
                )
            else:
                report.error(
                    "Lingoona 변수 누락",
                    f"{key}: 인자 {sorted(en_args - ko_args)} 없음 — en {sorted(en_sigs)} / ko {sorted(ko_sigs)}",
                )
        if ko_args - en_args:
            report.error(
                "Lingoona 잉여 변수",
                f"{key}: 원문에 없는 인자 {sorted(ko_args - en_args)} — ko {sorted(ko_sigs)}",
            )
        if en_args == ko_args and en_sigs != ko_sigs:
            report.warning(
                "Lingoona 태그 구조 변경",
                f"{key}: en {sorted(en_sigs.elements())} / ko {sorted(ko_sigs.elements())}",
            )
        # 온전한 태그 밖에 남은 홀수 꺾쇠 (<<1> 같은 오타) — 원문에 있는 만큼은 허용
        en_residue = LINGOONA_RE.sub("", en_value)
        ko_residue = LINGOONA_RE.sub("", ko_value)
        if ko_residue.count("<<") != en_residue.count("<<") or ko_residue.count(
            ">>"
        ) != en_residue.count(">>"):
            report.error("깨진 << >> 꺾쇠", f"{key}: {ko_value[:80]!r}")

        en_rich = rich_tag_counts(en_value)
        ko_rich = rich_tag_counts(ko_value)
        if not paired_tags_balanced(ko_rich):
            if paired_tags_balanced(en_rich):
                report.error("리치 태그 짝 안 맞음", f"{key}: {ko_value[:60]!r}")
            else:
                report.warning("리치 태그 짝 안 맞음(원문도 동일)", key)
        elif en_rich != ko_rich:
            report.warning(
                "리치 태그 개수 원문과 다름",
                f"{key}: en {sorted(en_rich.items())} / ko {sorted(ko_rich.items())}",
            )

        if en_value.count("\\n") != ko_value.count("\\n"):
            report.warning(
                "\\n 개수 다름",
                f"{key}: en {en_value.count('\\n')} / ko {ko_value.count('\\n')}",
            )

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="경고도 실패로 취급")
    parser.add_argument(
        "--verbose", action="store_true", help="항목 전체 출력 (기본 30건 제한)"
    )
    args = parser.parse_args()

    failed = False
    for english_path, ko_path in FILE_PAIRS:
        if not ko_path.exists():
            print(
                f"== {ko_path.name}: 파일 없음 — GameData의 ko 사전이 번역 원본이다 =="
            )
            failed = True
            continue
        report = validate_pair(english_path, ko_path, args.verbose)
        keys = len(parse_dictionary(english_path).mapping())
        print(f"== {ko_path.name} ↔ {english_path.relative_to(REPO_ROOT)} ==")
        report.print()
        print(
            f"  요약: 키 {keys}개 검사 — 오류 {report.error_count}건, 경고 {report.warning_count}건"
        )
        if report.error_count or (args.strict and report.warning_count):
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
