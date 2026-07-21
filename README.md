# KSP Korean Localization (한글패치)

**Kerbal Space Program 1.12.x** 본체와 **Making History·Breaking Ground DLC**의 한국어 번역 패치입니다.

KSP는 한국어를 공식 지원하지 않기 때문에, 이 패치는 원본 파일을 전혀 수정하지 않고
플러그인이 KSP에 새 언어 `ko`를 등록한 뒤 실행 즉시 전환하는 방식으로 동작합니다.

## ✨ 특징

- **원본 무수정** — 스팀 파일 무결성 검사에 안전하며, KSP 업데이트로 번역이 깨지지 않습니다.
- ModuleManager 등 **다른 모드 불필요**.
- 본체(Making History 포함) **12,030개** + Breaking Ground **724개** 문자열 번역 수록.
- **Pretendard 한글 폰트 내장** — 한글 전 음절(11,172자)과 자모를 커버해,
  텍스트 입력 시 낱자(ㄱ, ㅏ...)나 희귀 음절(뷁 등)도 깨지지 않습니다.
- DLC 미보유 시에도 무해합니다. (해당 문자열이 로드되지 않을 뿐)

## 🚀 설치

### CKAN 설치 (권장)

1. [CKAN](https://github.com/KSP-CKAN/CKAN/releases)을 실행합니다.
2. "KSP Korean Localization"을 검색해 체크합니다.
3. **Apply changes**를 눌러 설치합니다. 이후 업데이트도 CKAN이 자동으로 관리합니다.

> CKAN 등록 준비 중입니다. 등록 전까지는 아래 수동 설치를 이용해 주세요.

### 수동 설치

1. [Releases](https://github.com/synml/KSP-Korean-Localization/releases)에서 최신 zip을 내려받습니다.
2. 압축을 풀어 `GameData/KSPKorean` 폴더를 KSP 설치 폴더의 `GameData` 안에 넣습니다.
3. KSP를 실행하면 자동으로 한국어가 적용됩니다.

**제거:** `GameData/KSPKorean` 폴더를 삭제하면 즉시 영어로 복원됩니다.

## ⚠️ 알려진 제한

- KSP를 켤 때 로딩 화면에 `korean.fnt` 파일명이 잠깐 표시될 수 있습니다.  
  KSP가 폰트 번들을 로드하는 정상 과정입니다.

## 🐛 제보 및 기여

- 한글이 `□`로 표시되는 곳이나 오역·미번역을 발견하면 스크린샷과 함께
  [이슈](https://github.com/synml/KSP-Korean-Localization/issues)로 제보해 주세요.
- 번역 개선 PR도 환영합니다. 용어는 [docs/glossary.md](docs/glossary.md)를 따릅니다.

## 🛠️ 개발

- 번역 원본: `GameData/KSPKorean/Localization/*.ko.cfg` — `Localization { ko { ... } }` 구조.
- 번역 파일 규격: UTF-8 BOM + CRLF + 탭 들여쓰기, 한 키당 한 줄.
  `<<1>>` 등 변수 태그와 `<b>` 등 리치 텍스트 태그는 보존해야 합니다. (위치 이동은 가능)
- `reference_english/`는 대조용 영어 원문입니다. (수정 금지)
- 파이썬 도구는 [uv](https://docs.astral.sh/uv/)로 관리합니다. (최초 1회 `uv sync`)
- 커밋 전 검증(필수):

  ```bash
  uv run python scripts/validate.py
  ```

  키 누락, Lingoona 변수 태그(`<<1>>`) 훼손, 리치 텍스트 태그 짝, 값 내 `//`·중괄호 등을 검사합니다.

- 그 외 스크립트
  - `scripts/build_font.py`: 내장 폰트 `korean.fnt`를 재생성합니다.
    (Unity 에디터 불필요, KSP 설치본과 Pretendard OTF 필요 — 사용법은 docstring 참조)
  - `scripts/extract_glossary.py`: 용어집 작업용 용어 추출 도구입니다.
- 플러그인 빌드: Visual Studio에서 `KSP-Korean-Localization.sln`을 엽니다.  
  KSPBuildTools(NuGet)가 KSP 어셈블리를 실제 KSP 설치본에서 참조하므로 **빌드하려면 KSP가
  설치되어 있어야 합니다** (Steam 기본 경로는 자동 탐지, 그 외에는 `KSP_ROOT` 환경 변수로 지정).
- 릴리스는 `v*.*.*` 태그 push 시 GitHub Actions가 자동 생성합니다.
- 루트의 `KSPKoreanLocalization.netkan`은 CKAN 배포용 메타데이터 원본입니다.

## 📜 라이선스

- 이 패치: [MIT](LICENSE)
- 내장 폰트 [Pretendard](https://github.com/orioncactus/pretendard): SIL Open Font License 1.1
  - 전문은 [GameData/KSPKorean/LICENSE-Pretendard.txt](GameData/KSPKorean/LICENSE-Pretendard.txt)
