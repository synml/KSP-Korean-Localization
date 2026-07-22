# KSP-Korean-Localization

Kerbal Space Program(1.12.x) 본체 + 전체 DLC(Making History·Breaking Ground) 한국어 번역 패치.
KSP는 최종 버전(1.12.5)까지 한국어를 공식 지원하지 않으므로, 비공식 언어를 주입하는 방식으로 구현한다.

- 리포: <https://github.com/synml/KSP-Korean-Localization>
- 라이선스: MIT

## 현재 리포 상태

```python
reference_english/dictionary.en.cfg     # 원본 en-us 사전 (본체+Making History, 12,040줄) — 번역 대조용 원문 (불변)
reference_english/BreakingGround.en.cfg # 원본 en-us 사전 (Breaking Ground, 731줄) (불변)
GameData/KSPKorean/Localization/        # ★ 번역 원본(canonical) — dictionary.ko.cfg + BreakingGround.ko.cfg
KSPKorean/                              # C# 플러그인 (ko 등록/전환)
scripts/                                # validate.py(커밋 전 필수), build_font.py(폰트 번들), extract_glossary.py, untranslated.py(미번역 목록), ksploc.py(공용 파서)
docs/                                   # 용어집, 리뷰 체크리스트
install.cmd                             # 수동 설치 도우미 (cmd+PowerShell 하이브리드, 릴리스 자산으로 첨부)
KSPKoreanLocalization.netkan            # CKAN 제출용 메타데이터 (YAML) — 이 파일이 원본
pyproject.toml / uv.lock / .venv        # uv 프로젝트 (파이썬 의존성 + ruff)
```

용어·문장은 docs/glossary.md를 유일 기준으로 독자 관리한다.
**번역 수정·추가는 GameData 쪽 파일에 직접 한다.**
파일 규격: UTF-8 BOM + CRLF + 탭 들여쓰기 (reference_english 원본과 동일).

## 아키텍처 (런타임 언어 주입)

원본 파일을 건드리지 않고, 게임에 새 언어 `ko`를 등록한 뒤 런타임에 전환한다.
KSP 설정 UI는 내장 언어만 노출하지만 `Localizer.SwitchToLanguage()`는 임의 언어 태그를 받는다.

```python
GameData/KSPKorean/
├── Localization/
│   ├── dictionary.ko.cfg               # Localization { ko { #autoLOC_XXX = ... } }
│   └── BreakingGround.ko.cfg
├── korean.fnt                          # Pretendard 한글 TMP 폰트 번들 (scripts/build_font.py로 생성)
└── KSPKorean.version.versiontemplate   # KSP-AVC 버전 파일 템플릿 (CI가 버전 치환)
KSPKorean/                              # C# 플러그인 소스 (net472)
├── KSPKorean.csproj                    # SDK 스타일 + KSPBuildTools 1.1.1, 출력 → GameData/KSPKorean/
├── Localization.cs
└── Properties/AssemblyInfo.cs
```

플러그인 핵심 (실제 구현은 KSPKorean/Localization.cs):

```csharp
[KSPAddon(KSPAddon.Startup.Instantly, false)]
public class Localization : MonoBehaviour
{
    public void Awake()
    {
        if (!Application.isPlaying) return;
        var fontLoader = FindObjectOfType<FontLoader>();
        // LoadedFonts에서 korean/korean2 검색 → 없으면 GameData/KSPKorean/korean.fnt를 직접 로드
        var fonts = LoadKoreanFonts(fontLoader);
        if (fontLoader != null && fonts.Length > 0)
        {
            fontLoader.AddGameSubFont("ko", false, fonts);
            fontLoader.AddMenuSubFont("ko", false, fonts);
            fontLoader.SwitchFontLanguage("ko");
        }

        Localizer.SwitchToLanguage("ko");  // 이 한 줄이 언어 주입의 핵심
    }
}
```

이 방식의 장점: 원본 무결성 유지, ModuleManager 의존 없음, 스팀 파일 검증에 안전,
CKAN 배포 시 GameData 폴더 하나만 복사하면 끝.

## 폰트 — Pretendard 번들 동봉 (korean.fnt)

게임 내장 아틀라스(`NotoSansCJK-K01/K02-Regular`)는 일반 문장은 렌더링하지만
**호환 자모(U+3131~U+3163)가 없어 IME 조합 낱자가 □로 깨진다**. 이를 Pretendard 기반
`korean.fnt` 번들로 해결한다.

- 재생성: `scripts/build_font.py` (사용법·규약은 docstring). **Unity 에디터 불필요** —
  스톡 `GameData/Squad/KSPedia/kspfonts.ksp`를 템플릿 삼아 UnityPy로 에셋을 교체하는 방식.
  입력으로 KSP 설치본과 Pretendard static OTF가 필요.
- 구성 — 2단 폰트로 한글 전 음절 11,172자 + 자모 커버, 둘 다 68px 동일 품질 (LZ4 번들 약 10.5MB):
  - `korean`: KS X 1001 완성형 2,350자 + 호환 자모 51자, 68px SDF(spread 8), 4096² Alpha8
  - `korean2`: 나머지 음절 8,822자(뷁 등), 68px SDF(spread 8), 8192² Alpha8 (DX10.1+ GPU 필요).
    korean의 fallbackFontAssets가 korean2를 가리키고, 플러그인도 둘 다 서브폰트로 등록.
    텍스처 메모리 합계 80MB.
- KSP의 TMP는 레거시 1.x 직렬화(`m_fontInfo`/`m_glyphInfoList`)다. 아틀라스 y는 위에서부터,
  메트릭 단위는 샘플링 px. **내부 CAB 이름은 스톡과 달라야 한다** (같으면 둘 중 하나 로드 실패).
- 로딩: **FontLoader가 부팅 초기에 GameData 전역의 `*.fnt`를 자동 로드**한다. 플러그인은
  LoadedFonts에서 이름으로 찾아 `AddGameSubFont`/`AddMenuSubFont("ko")` +
  `SwitchFontLanguage("ko")`로 연결하고, 자동 로드 실패 시에만 번들을 직접 연다.
- 라이선스: Pretendard는 SIL OFL 1.1(RFN "Pretendard") — 에셋명이 "korean"이라 RFN 저촉 없음.
  OFL 전문을 `GameData/KSPKorean/LICENSE-Pretendard.txt`로 동봉 (배포 의무).
- **주의**: 이 번들의 폰트가 'ko' 서브폰트가 되면 내장 CJK 폴백을 대체하므로, 커버리지를
  줄이면 빠진 음절이 곧바로 □가 된다.

## 번역 파일 규칙

- 노드 구조: `Localization { ko { #autoLOC_XXXXXX = 값 } }`. 인코딩 UTF-8 (BOM 유무는 게임이 둘 다 허용).
- `<<1>>`, `<<A:1>>` 등 Lingoona 변수 태그는 절대 삭제/변형 금지. 한국어 어순에 맞춰 문장 내 위치 이동은 가능.
- `<b>`, `<color=#...>` 등 리치 텍스트 태그, `\n`(문자 그대로 백슬래시+n) 보존.
- 한 키당 한 줄. 값에 실제 개행 금지. 값 안의 `//`는 주석으로 파싱되어 잘리므로 주의.
- Lingoona 선택 태그 `<<n:1[a/b/c]>>`의 대괄호 안 형태는 번역 대상(validate는 형태 개수만 비교).
  단, 빈 형태 2개 연속(`//`)은 주석으로 잘리므로 ` / / `처럼 공백을 채울 것.
- 키 집합은 reference_english/ 원문과 1:1 일치해야 함 (키 누락 시 해당 문자열이 영어 fallback이 아니라 키 원문 노출).
- 본체·BG 사전에 **공통 키**가 있다 (8014149~8014151): 값 수정 시 두 파일 모두 반영할 것.

## 검증 자동화 (scripts/validate.py — 커밋 전 필수)

인게임 로딩은 느리므로, 커밋 전 스크립트 검증을 기본으로 한다:

1. reference_english/ ↔ ko cfg 키 집합 일치 여부 (누락/잉여 키 리포트)
2. 원문과 번역문의 `<<N>>`, `<<A:N>>` 태그 집합 일치 여부
3. 리치 텍스트 태그 짝 맞춤, 값 내 `{`/`}`/`//` 검출
4. cfg 문법 파싱 (중괄호 균형)
5. 한국어 맞춤법·용어 (ko 값 자체): 용어 이형(워프·매뉴버·쓰로틀 등 glossary 표준
   강제)·확정 오타(되서·안돼·몇일 등)·의존명사 띄어쓰기(종성 ㄹ + 수/때/것, `때문`).
   **'항상 틀린' 형태만 오류로 등록**(오탐이 커밋을 막지 않도록). 규칙은 `SPELL_BANNED`·
   `korean_spelling_issues`, 오탐 방지 allowlist는 `_DEP_NOUN_ALLOW`, 의도적 예외는
   `SPELLING_WAIVERS`. 새 '규칙형' 오류를 발견하면 여기에 편입한다.

Python으로 작성. 검증 통과 = 커밋 가능, 최종 확인은 인게임.

파이썬 도구는 uv 프로젝트로 관리한다: 의존성은 pyproject.toml, 실행은 `uv sync` 후
`uv run python scripts/<스크립트>`. 포매팅은 ruff 기본 설정(`uv run ruff format scripts`,
커스텀 설정 없음).

## 빌드 & 릴리스

- `.github/workflows/build.yml`: 태그(`v*.*.*`) push 시 KSPModdingLibs/KSPBuildTools 액션으로
  버전 치환(update-version) → 플러그인 컴파일(compile) → zip 어셈블(assemble-release, ARTIFACTS:
  GameData LICENSE\* README\*) → `softprops/action-gh-release@v3`로 릴리스 생성 (자산: zip +
  KSPKorean.version, install.cmd). 릴리스 생성은 assemble-release 액션의 `artifact-zip-path` 출력을 쓴다.
  `install.cmd`를 릴리스 자산으로 붙이는 이유는 raw.githubusercontent가 `text/plain`+nosniff로 응답해
  브라우저에서 다운로드가 아니라 표시되기 때문 — 릴리스 자산이라야 원클릭 링크
  (`releases/latest/download/install.cmd`)가 파일명 그대로 저장된다. **자산 이름을 바꾸면 안 된다.**
  UTF-8(BOM 없음)+CRLF 유지 — `.gitattributes`의 `*.cmd text eol=crlf`가 강제한다.
  구조는 cmd 스텁이 자기 파일을 UTF-8로 읽어 `#:PSBEGIN` **마지막** 등장 이후를 PowerShell로 실행
  (LastIndexOf여야 함 — 스텁 자신에 마커 문자열이 들어 있다). **사용자는 cmd만 받는 전제**이므로 zip은
  항상 GitHub 최신 릴리스에서 내려받아 설치 후 지운다(인자 `%1`은 관리자 권한 재실행 시 재다운로드를
  피하려는 내부 용도). KSP 경로는 Steam 레지스트리+libraryfolders.vdf와 관용 경로에서 탐지한다.
- **csproj는 SDK 스타일 + PackageReference(KSPBuildTools 1.1.1) 필수.** 구식 packages.config는
  현행 compile 액션의 `dotnet restore`가 복원하지 못해 리눅스에서 MSB3644로 실패한다. KSPBuildTools는
  프레임워크 참조 어셈블리 탐색을 끄고 System/Unity/게임 어셈블리를 전부 KSP Managed 폴더
  (`KSPBT_ManagedPath`)에서 직접 참조하므로, 패키지만 복원되면 리눅스 net472 빌드가 된다. 출력 경로
  기본값(`KSPBT_ModRoot` = `../GameData/<프로젝트명>/`)이 우리 레이아웃과 일치.
- zip 내부는 `GameData/KSPKorean/...` 구조.
- 버전 파일은 `.versiontemplate`에 `@VERSION_MAJOR@` 등 플레이스홀더, CI가 태그에서 파싱해 치환.

## CKAN 등록

netkan 실물은 리포 루트 `KSPKoreanLocalization.netkan` — **그 파일이 원본이므로 여기에 사본을
두지 않는다** (과거 드리프트 발생). 형식 기준은 linuxgurugamer의 netkan들
(BetterTimeWarpCont, ToolbarController 등): YAML, `$kref`(github) +
`$vref: '#/ckan/ksp-avc'`(KSP 호환 버전을 릴리스 자산의 KSPKorean.version에서 자동 추적),
`tags: [plugin]`, `install: find KSPKorean → GameData`. spec_version·author·resources 등은
봇이 유도하므로 생략. 플러그인 방식이므로 ModuleManager `depends` 불필요. DLC 번역은
미보유자에게도 무해(해당 키가 로드되지 않을 뿐)하므로 단일 패키지로 배포.

NetKAN PR: [KSP-CKAN/NetKAN#11379](https://github.com/KSP-CKAN/NetKAN/pull/11379).

## 번역 스타일 가이드

- 용어집을 `docs/glossary.md`로 먼저 정리하고 전체 파일에 일관 적용.
- 커뮤니티에서 영어로 통용되는 용어(Delta-v 등)는 억지 한글화하지 않는다.
- 문체: 파트 설명 "~합니다"체, 튜토리얼 "~하세요"체로 유형별 통일.
- 과학 리포트 블록(1인칭 관찰·시료·측정 로그)은 평서체(일지 어조)를 유지 — 파트 설명체와 별개 레지스터.
- KSP 특유의 유머·말장난은 직역하지 않고 정보(스펙/경고)만 보존한 재창작 허용.
- UI 라벨은 잘림 방지를 위해 최대한 압축.

## 미번역 유지(ko==en) 정책

번역 완료 상태다. 남은 `ko==en`은 전부 **의도적 유지**이며 재번역 대상이 아니다. 기준선은
`uv run python scripts/untranslated.py`로 확인. 유지 대상:

- **파트 검색 태그**(keyword 버킷) — 번역 금지(원문 유지).
- **단위/기호/약어/모델·기체명**(symbol 버킷) — Δv, ` m²`, MET:, [CTRL] 등.
- 검색 태그 라인 누수(`e/c`·`a.r.m`·`1.875` 등 keyword 휴리스틱 문자셋을 벗어난 것).
- 시나리오 전용 기체·고유명(Starbeam, ESA MPO/MMO/MSE 등), 실제 로켓 실명(Titan II GLV 등).
- MB 내부 노드 식별자(Mx_DIALOGn·DIALOG_NEW1), 열/디버그 내부 라벨(CoreEnergy·RadSat 등),
  제품명(Making History).
- **준영문 위장 키 주의**: 둥근따옴표를 곧은따옴표로 정규화해 둔 탓에 `ko≠en`이지만 실제로는 영어인
  키가 과거 존재했다. untranslated.py는 이를 못 잡는다(전량 처리 완료). 재발 시 탐지법:
  `ko≠en`이면서 한글이 없고 latin 4자+ 단어가 있는 값을 나열.

## 영어 원문 결함 (번역도 그대로 재현 — 회귀 금지)

영어 원문 자체 결함은 번역에서도 그대로 둔다(동작 동일성). validate는 번역본이 동일 결함을
재현해야 통과하므로, 나중에 "고치는" 회귀를 막기 위해 목록을 남긴다. Lingoona 의도적 단순화
예외는 scripts/validate.py의 `LINGOONA_WAIVERS`에 근거와 함께 기록.

- **#autoLOC_190902** (dictionary.en.cfg:652): `<<1>` — Lingoona 태그 닫는 꺾쇠 하나 누락
  (정상은 `<<1>>`). 값에서 그대로 노출된다. 번역도 `<<1>` 형태 유지(validate 태그 집합 비교 통과 조건).
- **#autoLOC_6002660** (dictionary.en.cfg:7763): 닫는 색상 태그가 `<\color>` — 슬래시가 아니라
  **역슬래시**(정상은 `</color>`). 이후 텍스트가 계속 주황색으로 남는다. RICH_TAG_RE는 `</`만 close로
  세므로 en·ko 양쪽에서 무시되어 validate 통과. 번역도 `<\color>` 그대로 보존.
- **#autoLOC_7000003** (dictionary.en.cfg:8491): `<<o:2>>`가 문장에서 실질 의미 없이 삽입됨.
  한국어에서 생략 → `LINGOONA_WAIVERS`에 등록.
- **철자 오타**(동작 무관, 번역이 한글이라 무해 — 기록만): #autoLOC_190902 `occured`,
  #autoLOC_259361(dictionary.en.cfg:1256) `Receieved`.

## 개발 원칙

- 원본(reference_english/)은 대조용 불변 자료로 취급, 수정 금지.
- 대량 수정은 손으로 하지 말고 일회성 스크립트로 수행한다(재현 가능·검증 용이). 일회성 스크립트
  (apply_*·unify_* 등)는 반영 후 삭제하고, 변경 이력은 git 커밋으로 추적한다. 상시 도구
  (validate.py·build_font.py·untranslated.py 등)만 scripts/에 보존한다.
