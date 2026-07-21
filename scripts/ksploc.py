"""KSP Localization dictionary.cfg 공용 파서/라이터.

KSP ConfigNode 문법 중 로컬라이제이션 사전이 쓰는 서브셋만 다룬다:

    Localization
    {
        <lang>            // 노드 이름 뒤 주석 허용
        {
            #autoLOC_XXX = 값
        }
    }

게임(ConfigNode.PreFormatConfig)과 동일한 규칙을 적용한다:
- 줄 어디서든 ``//`` 이후는 주석으로 제거된다 (값 안에 있어도 잘린다).
- ``=`` 좌우 공백은 Trim된다.
- 키는 대소문자를 구분한다 (#autoLOC_ / #autoLoc_ 혼재).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path


class CfgError(Exception):
    """cfg 구조가 기대와 다를 때."""


@dataclass
class Entry:
    key: str
    value: str  # 주석 제거 + strip 적용된, 게임이 실제로 보는 값
    line_no: int
    comment: str | None  # 값 뒤에 붙어 있던 // 주석 (없으면 None)


@dataclass
class Dictionary:
    path: Path
    language: str
    header_comment: str | None  # 언어 노드 이름 줄에 붙어 있던 주석
    entries: list[Entry]

    def mapping(self) -> dict[str, str]:
        """키 → 값. 중복 키는 첫 값이 이긴다 (중복 자체는 duplicates()로 확인)."""
        m: dict[str, str] = {}
        for e in self.entries:
            m.setdefault(e.key, e.value)
        return m

    def duplicates(self) -> dict[str, int]:
        counts = Counter(e.key for e in self.entries)
        return {k: n for k, n in counts.items() if n > 1}


def parse_dictionary(path: str | Path) -> Dictionary:
    path = Path(path)
    text = path.read_bytes().decode("utf-8-sig")

    depth = 0  # 0: 파일 최상위, 1: Localization 내부, 2: 언어 노드 내부
    pending_name: str | None = None
    pending_comment: str | None = None
    language: str | None = None
    header_comment: str | None = None
    entries: list[Entry] = []

    for line_no, raw in enumerate(text.splitlines(), start=1):
        comment: str | None = None
        line = raw
        if "//" in line:
            line, comment = line.split("//", 1)
        line = line.strip()

        if not line:
            continue

        if line == "{":
            if pending_name is None:
                raise CfgError(f"{path}:{line_no}: 노드 이름 없이 '{{'가 나타남")
            if depth == 0:
                if pending_name != "Localization":
                    raise CfgError(
                        f"{path}:{line_no}: 최상위 노드가 Localization이 아님: {pending_name!r}"
                    )
            elif depth == 1:
                if language is not None:
                    raise CfgError(
                        f"{path}:{line_no}: 언어 노드가 두 개 이상임 ({language!r}, {pending_name!r})"
                    )
                language = pending_name
                header_comment = pending_comment
            else:
                raise CfgError(
                    f"{path}:{line_no}: 언어 노드 내부에 하위 노드 {pending_name!r}"
                )
            depth += 1
            pending_name = None
            pending_comment = None
        elif line == "}":
            if pending_name is not None:
                raise CfgError(
                    f"{path}:{line_no}: 노드 이름 {pending_name!r} 뒤에 '{{'가 없음"
                )
            depth -= 1
            if depth < 0:
                raise CfgError(f"{path}:{line_no}: 짝이 없는 '}}'")
        elif "=" in line:
            if depth != 2:
                raise CfgError(f"{path}:{line_no}: 언어 노드 밖에서 키=값 발견")
            key, value = line.split("=", 1)
            entries.append(
                Entry(
                    key=key.strip(),
                    value=value.strip(),
                    line_no=line_no,
                    comment=comment.strip() if comment is not None else None,
                )
            )
        else:
            if pending_name is not None:
                raise CfgError(
                    f"{path}:{line_no}: 노드 이름 {pending_name!r} 뒤에 '{{'가 없음"
                )
            if depth >= 2:
                raise CfgError(f"{path}:{line_no}: '='가 없는 값 줄: {line!r}")
            pending_name = line
            pending_comment = comment.strip() if comment is not None else None

    if depth != 0:
        raise CfgError(f"{path}: 중괄호가 닫히지 않음 (최종 깊이 {depth})")
    if language is None:
        raise CfgError(f"{path}: 언어 노드를 찾지 못함")

    return Dictionary(
        path=path, language=language, header_comment=header_comment, entries=entries
    )


def write_dictionary(
    path: str | Path, language: str, pairs: list[tuple[str, str]]
) -> None:
    """reference_english 원본과 동일한 규격으로 저장: UTF-8 BOM, CRLF, 탭 들여쓰기."""
    path = Path(path)
    lines = ["Localization", "{", f"\t{language}", "\t{"]
    lines.extend(f"\t\t{key} = {value}" for key, value in pairs)
    lines.extend(["\t}", "}"])
    data = "\r\n".join(lines) + "\r\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xef\xbb\xbf" + data.encode("utf-8"))


# 리포 루트 기준 (영어 원문, 번역본) 파일 쌍. validate/extract_glossary가 공용으로 쓴다.
REPO_ROOT = Path(__file__).resolve().parent.parent
FILE_PAIRS = [
    (
        REPO_ROOT / "reference_english" / "dictionary.en.cfg",
        REPO_ROOT / "GameData" / "KSPKorean" / "Localization" / "dictionary.ko.cfg",
    ),
    (
        REPO_ROOT / "reference_english" / "BreakingGround.en.cfg",
        REPO_ROOT / "GameData" / "KSPKorean" / "Localization" / "BreakingGround.ko.cfg",
    ),
]
