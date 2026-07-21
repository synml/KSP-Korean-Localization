# KSP 한국어 용어집

번역 전체에 일관 적용하는 용어 기준.

- 근거 데이터: `python scripts/extract_glossary.py` (reference_english ↔ GameData ko 값 대조 추출)
- 표기 원칙
  1. 커뮤니티에서 영어로 통용되는 용어(Delta-v, SAS, RCS, Mk1 등 모델명)는 억지 한글화하지 않는다.
  2. 인명·천체명은 음차하고, Lingoona 성별 접미사(`^N` 등)는 그대로 보존한다.
  3. 이형 표기가 혼재하면 아래 "표준"으로 통일한다. 신규 번역은 즉시 표준형을 쓴다.
  4. 변수(`<<1>>`) 뒤 조사는 병기한다: `(을)를`, `(이)가`, `(은)는`, `(과)와`, `(으)로` — Lingoona가 한국어 조사를 지원하지 않기 때문이다.
  5. 영어 병기는 `한국어(English)` 형태로 하고, 조사는 괄호에 바로 붙인다: "순행 방향(Prograde)으로". 병기는 튜토리얼 첫 등장 등 이해를 돕는 곳에만 쓴다.
- 문체
  - 파트 설명·미션 개요: **~합니다**체
  - 튜토리얼·안내: **~하세요**체
  - UI 라벨·버튼: 명사형으로 최대 압축 (잘림 방지). 예: "기체 회수", "빠른 저장"
  - KSP 특유의 유머는 정보(스펙·경고)를 보존하는 선에서 재창작 허용.

## 조종·비행

| English                | 표준 한국어         | 비고                                                                                             |
| ---------------------- | ------------------- | ------------------------------------------------------------------------------------------------ |
| Stability Assist       | 안정성 보조         |                                                                                                  |
| Prograde               | 순행                | SAS 마커 라벨은 "순행 방향"                                                                      |
| Retrograde             | 역행                | SAS 마커 라벨은 "역행 방향"                                                                      |
| Normal / Anti-Normal   | 법선 / 반법선       | SAS 마커 라벨은 "법선 방향 / 반법선 방향"                                                        |
| Radial In / Radial Out | 구심 / 원심         | SAS 마커 라벨은 "구심 방향 / 원심 방향"                                                          |
| Maneuver               | 메뉴버              | 커뮤니티 통용 표기                                                                               |
| Maneuver Node          | 메뉴버 노드         |                                                                                                  |
| Target                 | 목표                |                                                                                                  |
| Throttle               | 스로틀              | 표준 스로틀(79키). 일부 UI 라벨·설명은 "출력" 유지 허용(6키, 예: "발사 시 엔진 기본 출력")       |
| Thrust                 | 추력                |                                                                                                  |
| Pitch / Yaw / Roll     | 피치 / 요 / 롤      | "~컨트롤"은 "~ 제어"                                                                             |
| SAS / RCS              | SAS / RCS           | 영어 유지                                                                                        |
| Navball                | 항법구              |                                                                                                  |
| EVA                    | EVA                 | 영어 유지(복합어 포함). 예외: "Let go"는 "EVA 시작"으로 의역, 튜토리얼 약어 풀이 병기 1곳은 유지 |
| Brakes                 | 제동장치            |                                                                                                  |
| (Landing) Gear         | 착륙장치            |                                                                                                  |
| Lights                 | 조명장치            |                                                                                                  |
| Abort                  | 비상탈출            |                                                                                                  |
| Stage / Staging        | 스테이지 / 스테이징 |                                                                                                  |
| Trim                   | 트림                |                                                                                                  |

## 궤도 역학

| English                     | 표준 한국어           | 비고                                                                                                                            |
| --------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Orbit                       | 궤도                  |                                                                                                                                 |
| Apoapsis / Periapsis        | 최원점 / 최근점       | 약어 Ap/Pe 허용                                                                                                                 |
| Inclination                 | 경사각                |                                                                                                                                 |
| Eccentricity                | 이심률                |                                                                                                                                 |
| Ascending / Descending Node | 승교점 / 강교점       |                                                                                                                                 |
| Rendezvous                  | 랑데부                |                                                                                                                                 |
| Docking / Undock            | 도킹 / 도킹 해제      |                                                                                                                                 |
| Transfer                    | 전이                  | 궤도 맥락. 자원/승무원 이동은 "이동"                                                                                            |
| Delta-v                     | Delta-v (Δv)          | 영어 유지. UI 축약은 Δv 허용                                                                                                    |
| Burn Time                   | 연소시간              |                                                                                                                                 |
| Time Warp / Physics Warp    | 시간 가속 / 물리 가속 | warp 단독·동사형도 "시간 가속"으로. "워프" 음차 금지. Increase/Decrease Time Warp 컨트롤 라벨은 "시간 가속/시간 감속" 대구 허용 |
| Trajectory                  | 궤적                  |                                                                                                                                 |
| Sub-Orbital                 | 준궤도                |                                                                                                                                 |
| Escape (trajectory)         | 탈출 (궤적)           |                                                                                                                                 |
| Encounter                   | 조우                  |                                                                                                                                 |
| Atmosphere                  | 대기                  | 층 강조 시 "대기권"                                                                                                             |
| Reentry                     | 재진입                |                                                                                                                                 |
| CommNet                     | 통신망                |                                                                                                                                 |
| SOI (Sphere of Influence)   | 영향권                | 일부 "중력권" 잔존 허용                                                                                                         |
| Flyby / Fly by              | 근접 통과             |                                                                                                                                 |
| Launch Window               | 발사 기회             |                                                                                                                                 |
| Parking Orbit               | 주차 궤도             |                                                                                                                                 |

## 기체·파트

| English                         | 표준 한국어                   | 비고                                       |
| ------------------------------- | ----------------------------- | ------------------------------------------ |
| Vessel / Craft                  | 기체                          |                                            |
| Ship                            | 우주선                        |                                            |
| Probe                           | 무인 탐사선                   | Satellite("인공위성")와 구분               |
| Satellite                       | 인공위성                      | Probe("무인 탐사선")와 구분                |
| Lander / Rover / Station / Base | 착륙선 / 로버 / 정거장 / 기지 |                                            |
| Debris                          | 잔해물                        |                                            |
| Part                            | 부품                          |                                            |
| Pods (파트 카테고리)            | 조종부                        | 개별 유인 파트는 "사령선"                  |
| Command Pod                     | 사령선                        |                                            |
| Command Module                  | 조종 모듈                     | 유·무인 조종 파트 총칭(엔지니어 리포트 등) |
| Decoupler / Separator           | 디커플러 / 세퍼레이터         | Stack=직렬형, Radial=방사형                |
| Fairing                         | 페어링                        |                                            |
| Heat Shield                     | 방열판                        | Radiator("방열기")와 구분                  |
| Radiator                        | 방열기                        | Heat Shield("방열판")와 구분               |
| Parachute                       | 낙하산                        |                                            |
| Drogue Chute                    | 보조 낙하산                   |                                            |
| Docking Port                    | 도킹 포트                     |                                            |
| Fuel Tank                       | 연료 탱크                     |                                            |
| Engine                          | 엔진                          |                                            |
| Vernier Engine                  | 버니어 엔진                   | 파트 고유명 Vernor는 "버너"                |
| Solar Panel                     | 태양전지                      |                                            |
| Battery                         | 배터리                        |                                            |
| Antenna                         | 안테나                        |                                            |
| Reaction Wheel                  | 자세 제어휠                   | RCS("반작용 제어")와 혼동 주의             |
| Control Surface                 | 조종면                        |                                            |
| Fuel Line                       | 연료관                        | Fuel Duct(FTX-2)도 "연료관"                |
| Strut                           | 스트럿                        |                                            |
| Landing Strut                   | 착륙 지지대                   | 착륙선 다리(Strut "스트럿"과 구분)         |
| Intake                          | 흡입구                        |                                            |
| Wheel                           | 바퀴                          | 액션그룹 라벨 "조향장치"는 문맥상 유지     |
| Ladder                          | 사다리                        |                                            |
| Grapple                         | 집게                          | AGU(고급 집게장치)·Klaw. "집게장치"        |

## 자원

| English         | 표준 한국어 | 비고 |
| --------------- | ----------- | ---- |
| Liquid Fuel     | 액체연료    |      |
| Oxidizer        | 산화제      |      |
| Solid Fuel      | 고체연료    |      |
| Monopropellant  | 단일추진제  |      |
| Electric Charge | 전력        |      |
| Ore             | 광물        |      |
| Xenon Gas       | 제논 가스   |      |
| Ablator         | 융제재      |      |
| Intake Air      | 흡입 공기   |      |
| EVA Propellant  | EVA 추진제  |      |

## 과학·커리어

| English                  | 표준 한국어                | 비고                        |
| ------------------------ | -------------------------- | --------------------------- |
| Science                  | 과학점수                   | 게임 모드명은 "과학 모드"   |
| Funds                    | 자금                       |                             |
| Reputation               | 평판                       |                             |
| Contract                 | 계약                       |                             |
| Experiment               | 실험                       |                             |
| Crew Report / EVA Report | 승무원 보고서 / EVA 보고서 |                             |
| Surface Sample           | 지표면 시료                |                             |
| Biome                    | 생물군계                   | terrain("지형")과 구분      |
| Situation                | 상황                       |                             |
| Recover                  | 회수                       |                             |
| Transmit                 | 전송                       |                             |
| Strategy                 | 전략                       |                             |
| Milestone                | 마일스톤                   | Achievements("업적")와 구분 |
| World First              | 세계 최초 기록             |                             |
| Tech Tree / Technology   | 기술 트리 / 기술           |                             |
| Mystery Goo              | 신비한 구                  | 부품명은 "신비한 구 보관함" |
| Outpost                  | 전초기지                   | Base("기지")와 구분         |

## 시설 (KSC)

| English                         | 표준 한국어         | 비고                                                                        |
| ------------------------------- | ------------------- | --------------------------------------------------------------------------- |
| Kerbal Space Center (KSC)       | 커벌 우주 센터      | 약칭 KSC 유지                                                               |
| Vehicle Assembly Building (VAB) | 발사체 조립동       |                                                                             |
| Spaceplane Hangar (SPH)         | 비행기 격납고       |                                                                             |
| Runway                          | 활주로              |                                                                             |
| Launch Pad                      | 발사대              | KSC의 발사 시설(1개). Launch Site("발사장")와 구분                          |
| Launch Site / Launch Sites      | 발사장              | 시나리오·미션 빌더의 발사 지점(우메랑·사막 등). Launch Pad("발사대")와 구분 |
| Tracking Station                | 관제소              |                                                                             |
| Mission Control                 | 관제 센터           |                                                                             |
| Astronaut Complex               | 우주비행사 복합단지 |                                                                             |
| Research and Development (R&D)  | 연구개발 시설       |                                                                             |
| Administration Building         | 관리동              |                                                                             |

## 인물·종족

| English                           | 표준 한국어                   | 비고                    |
| --------------------------------- | ----------------------------- | ----------------------- |
| Kerbal                            | 커벌                          |                         |
| Kerman                            | 커맨                          |                         |
| Jebediah / Bill / Bob / Valentina | 제베디아 / 빌 / 밥 / 발렌티나 |                         |
| Pilot                             | 조종사                        | Autopilot은 "자동 조종" |
| Engineer                          | 기술자                        |                         |
| Scientist                         | 과학자                        |                         |
| Tourist                           | 관광객                        |                         |
| Crew                              | 승무원                        |                         |
| Kraken                            | 크라켄                        |                         |

## 천체 (음차 + `^N` 보존)

| English | 한국어 | English | 한국어 |
| ------- | ------ | ------- | ------ |
| The Sun | 태양   | Duna    | 듀나   |
| Moho    | 모호   | Ike     | 이케   |
| Eve     | 이브   | Dres    | 드레스 |
| Gilly   | 길리   | Jool    | 줄     |
| Kerbin  | 커빈   | Laythe  | 레이테 |
| The Mun | 문     | Vall    | 발     |
| Minmus  | 민무스 | Tylo    | 타일로 |
| Bop     | 밥     | Pol     | 폴     |
| Eeloo   | 일루   |         |        |

- 밥(Bop)이 인명 밥(Bob Kerman)과 동형. 혼동 시 "봅" 변경 후보이나 현행 유지.
- 값 끝 `^N`(성별 태그)을 지우면 안 된다.
- Munar = 뮤나 (고유명 요소, 예: Munar Excursion Module → 뮤나 여행 모듈). 일반 형용사 "munar orbit"은 "문 궤도".

## 비행 상태 (Situation)

| English   | 한국어      | English     | 한국어        |
| --------- | ----------- | ----------- | ------------- |
| LANDED    | 착륙함      | ORBITING    | 궤도 선회중   |
| SPLASHED  | 착수함      | ESCAPING    | 탈출중        |
| PRELAUNCH | 발사 준비중 | DOCKED      | 도킹함        |
| FLYING    | 비행중      | SUB-ORBITAL | 준궤도 비행중 |

## UI 공통

| English               | 표준 한국어               | 비고                                                                                                                                                                                                                                     |
| --------------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Save / Load           | 저장 / 불러오기           | 버튼은 "저장하기/불러오기" 허용                                                                                                                                                                                                          |
| Quicksave / Quickload | 빠른 저장 / 빠른 불러오기 | 파일명 키 `quicksave`는 번역 금지                                                                                                                                                                                                        |
| Revert (Flight)       | (비행) 되돌리기           |                                                                                                                                                                                                                                          |
| Recover Vessel        | 기체 회수                 |                                                                                                                                                                                                                                          |
| Terminate             | 종료하기                  |                                                                                                                                                                                                                                          |
| Launch                | 발사                      |                                                                                                                                                                                                                                          |
| Cancel                | 취소                      |                                                                                                                                                                                                                                          |
| Accept / OK           | 확인                      |                                                                                                                                                                                                                                          |
| Decline               | 거절                      | 계약 맥락 "계약 철회"                                                                                                                                                                                                                    |
| Delete                | 삭제                      |                                                                                                                                                                                                                                          |
| Apply                 | 적용                      |                                                                                                                                                                                                                                          |
| Rename                | 이름 변경                 |                                                                                                                                                                                                                                          |
| Settings              | 설정                      |                                                                                                                                                                                                                                          |
| Difficulty            | 난이도                    |                                                                                                                                                                                                                                          |
| Map View              | 지도 보기                 | 합성어 예외: 큐브맵·히트맵                                                                                                                                                                                                               |
| Docking Mode          | 도킹 모드                 |                                                                                                                                                                                                                                          |
| Waypoint              | 경유지                    |                                                                                                                                                                                                                                          |
| KerbNet               | 커브넷                    |                                                                                                                                                                                                                                          |
| Mission               | 미션 / 임무               | 문맥별 구분. 미션 빌더(MB) 기능·엔티티는 "미션"(미션 앱·점수·파일·노드·모드, ESA 협업 미션 등). 일반 명사(과업)는 "임무"(계약·스톡 튜토리얼·시나리오·파트 플레이버·mission flag 부품). 예외: MET="임무 경과 시간", 역사적 실제 미션 서술 |
| Mission Builder (MB)  | 미션 빌더                 |                                                                                                                                                                                                                                          |
| Missions App          | 미션 앱                   |                                                                                                                                                                                                                                          |
| Action Pane (MB)      | 액션 창                   | Settings AP=설정 액션 창(SAP), Graphical AP=그래픽 액션 창(GAP). 노드 분류·노드명의 Action도 "액션"                                                                                                                                      |

## Breaking Ground DLC

| English                 | 표준 한국어         | 비고 |
| ----------------------- | ------------------- | ---- |
| Robotics                | 로보틱스            |      |
| Hinge                   | 힌지                |      |
| Piston                  | 피스톤              |      |
| Rotor                   | 로터                |      |
| Rotation Servo          | 회전 서보           |      |
| Propeller / Blade       | 프로펠러 / 블레이드 |      |
| Grip Pad                | 그립 패드           |      |
| Deployed Science        | 전개형 과학장비     |      |
| Surface Features        | 지표면 특징         |      |
| Deploy / Retract        | 전개 / 수납         |      |
| KAL-1000 등 부품 고유명 | 영어 유지           |      |

## 파트 별명 음차 (따옴표 별명)

파트 제목의 별명은 따옴표를 유지한 채 음차하고, 튜토리얼·설명문에서도 동일 표기를 쓴다.

**따옴표 종류는 원문을 그대로 따른다** (원문이 큰따옴표·작은따옴표를 혼용함). 임의로 통일하지 말 것:

- 엔진·부스터·SRB 별명 등 대부분: **큰따옴표** — BACC "섬퍼", KS-25x4 "매머드", KE-1 "마스토돈", S2-33 "클라이즈데일", THK "폴룩스" 등.
- KV 귀환선 채소 별명: **작은따옴표** — KV-1 '어니언', KV-2 '피', KV-3 '포머그레넷' (원문 'Onion'·'Pea'·'Pomegranate').

전체 대응표:

| English    | 한국어       | English  | 한국어     | English      | 한국어     |
| ---------- | ------------ | -------- | ---------- | ------------ | ---------- |
| Ant        | 앤트         | Mainsail | 메인세일   | Spider       | 스파이더   |
| Bobcat     | 밥캣         | Mammoth  | 매머드     | Swivel       | 스위블     |
| Cheetah    | 치타         | Mastodon | 마스토돈   | Terrier      | 테리어     |
| Clydesdale | 클라이즈데일 | Mite     | 마이트     | Thoroughbred | 서러브레드 |
| Cub        | 컵           | Nerv     | 네르프     | Thud         | 서드       |
| Dart       | 다트         | Panther  | 판터       | Thumper      | 섬퍼       |
| Dawn       | 던           | Pollux   | 폴룩스     | Twin-Boar    | 트윈-보어  |
| Flea       | 플리         | Poodle   | 푸들       | Twitch       | 트위치     |
| Goliath    | 골리앗       | Puff     | 퍼프       | Vector       | 벡터       |
| Hammer     | 해머         | Reliant  | 릴라이언트 | Wheesley     | 위즐리     |
| Juno       | 주노         | Rhino    | 라이노     | Whiplash     | 위플래시   |
| Kickback   | 킥백         | Shrimp   | 슈림프     | Wolfhound    | 울프하운드 |
| Kodiak     | 코디악       | Skiff    | 스키프     | Vernor       | 버너       |
| Skipper    | 스키퍼       | Spark    | 스파크     |              |            |

### 규칙

- 기체 표시명은 영어로 유지한다. 기체 이름 자체는 번역하지 않는다.
- 시나리오 전용 기체명에서 고유명(Starbeam, Quietlands 등)에 붙은 **일반 명사부만** 번역한다:
  Lander 착륙선, Rover 로버, Probe 탐사선, Debris 잔해물, signal relay 신호 중계기, radio observatory 전파 관측소.
- 완전 일반명 기체(고유명이 없는 이름)도 번역하지 않고 영어로 유지한다:
  Space Station Core, Kerbal Rescuer, Retriever A1 등.

## 회사명 음차

| English       | 한국어         | English         | 한국어          |
| ------------- | -------------- | --------------- | --------------- |
| Rockomax      | 로코맥스       | Zaltonic        | 잘토닉          |
| Kerbodyne     | 커보다인       | Kerlington      | 커링턴          |
| Probodobodyne | 프로보도보다인 | Ionic Symphonic | 아이오닉 심포닉 |
| Stratus       | 스트라투스     | STEADLER        | 스테들러        |

이름 자체가 상표로 굳은 회사는 영어 유지:

| 상표 (영어 유지)          |
| ------------------------- |
| Periapsis Rocket Supplies |
| C7                        |
| O.M.B.                    |

이름을 번역한 회사는 음차 대상이 아니다:

| English                  | 한국어               |
| ------------------------ | -------------------- |
| FLOOYD Dynamics          | 플루이드 역학 연구소 |
| Experimental Engineering | 실험 공학 그룹       |
| C7 Aerospace             | C7 항공우주 사업부   |

## 영어 유지 목록 (한글화 금지)

| 항목                          | 비고                                 |
| ----------------------------- | ------------------------------------ |
| Delta-v (Δv)                  |                                      |
| SAS / RCS                     |                                      |
| ISP                           | 비추력 병기 가능                     |
| 파트 모델명                   | Mk1·LV-909 등                        |
| KAL-1000                      |                                      |
| quicksave                     | 저장 파일명 키                       |
| CFG 키·파일명                 | 전반                                 |
| 시나리오 전용 기체명 고유명부 | Starbeam 등                          |
| 확장팩 제품명                 | Making History·Breaking Ground       |
| 스톡 기체 표시명              | Hopper·Osprey·Dynawing·Kerbal 1–5 등 |
