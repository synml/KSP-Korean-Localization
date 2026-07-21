"""korean.fnt (Pretendard TMP 폰트 번들) 재생성 스크립트.

배경: KSP 내장 NotoSansCJK-K01/K02 아틀라스는 한글 음절만 있고 호환 자모
(ㄱ, ㅏ 등 U+3131~U+3163)가 없어, IME 조합 중 낱자가 □로 깨진다. 또한 이 번들의
폰트가 'ko' 언어 서브폰트가 되면 내장 CJK 폴백을 대체하므로, 한글 전체
11,172자를 직접 커버해야 한다 (안 하면 뷁 같은 완성형 밖 음절이 깨짐).

구성 — 2단 폰트 (둘 다 68px 동일 품질):
- korean  : KS X 1001 완성형 2,350자 + 호환 자모 51자, 68px SDF, 4096x4096
- korean2 : 나머지 음절 8,822자, 68px SDF, 8192x8192 (희귀 음절 커버)
  korean의 fallbackFontAssets가 korean2를 가리키고, 플러그인도 둘 다 서브폰트로 등록한다.
  참고: 8192 텍스처는 DX10.1+ GPU 요구 (KSP 1.12 구동 사양이면 충족).

방식: Unity 에디터 없이, 게임의 스톡 폰트 번들(GameData/Squad/KSPedia/kspfonts.ksp)을
템플릿으로 삼아 UnityPy로 에셋을 교체한다. NotoSans SDF 3종(폰트/머티리얼/아틀라스)은
korean으로, JD-LCD SDF 3종은 korean2로 재활용한다. 좌표·메트릭 규약은 템플릿 실측 기준:
- TMP 레거시(1.x) 포맷: m_fontInfo / m_glyphInfoList, 단위는 샘플링 px
- 아틀라스 y는 위에서부터, 글리프 사각형은 타이트 박스, SDF 경계 0.5, spread=Padding
- 머티리얼 _GradientScale = Padding + 1
- 내부 CAB 이름은 스톡과 충돌하지 않도록 반드시 고유값으로 변경 (동일 CAB 이름의
  번들 두 개는 동시 로드 불가)

FontLoader가 GameData 전역에서 *.fnt를 자동 로드하므로(부팅 초기, 로딩 화면에 파일명이
잠깐 표시되는 것이 이 단계) 플러그인은 LoadedFonts에서 이름으로 찾기만 하면 된다.

사용법 (Pretendard: https://github.com/orioncactus/pretendard 릴리스의 static OTF):
  uv sync   # 최초 1회 — 의존성은 pyproject.toml에 정의
  uv run python scripts/build_font.py --font <Pretendard-Regular.otf 경로> \
    --ksp "D:/SteamLibrary/steamapps/common/Kerbal Space Program"

출력: GameData/KSPKorean/korean.fnt
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import freetype
import numpy as np
import UnityPy
from scipy.ndimage import distance_transform_edt

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "GameData" / "KSPKorean" / "korean.fnt"

SS = 2  # 슈퍼샘플링 배율 (EDT 품질용). margin 공식이 SS=2 전제.

# kspfonts.ksp (KSP 1.12.5) 내 오브젝트 path_id
FONT1_PID = -1072048177199392412  # NotoSans-Regular SDF → korean
ATLAS1_PID = -7850919507734300745
MAT1_PID = -1051713240447717584
FONT2_PID = -1196214728388956942  # JD-LCD_rounded SDF → korean2
ATLAS2_PID = 4535983904748628244
MAT2_PID = -2103592330720330018
DEF_PID = -6447205430494472417  # kspfonts_bundle (KSPBundleDefinition TextAsset)
BUNDLE_PID = 1


def ksx1001_syllables() -> set[str]:
    chars = set()
    for lead in range(0xB0, 0xC9):
        for trail in range(0xA1, 0xFF):
            try:
                ch = bytes([lead, trail]).decode("cp949")
            except UnicodeDecodeError:
                continue
            if "가" <= ch <= "힣":
                chars.add(ch)
    return chars


def render_sdf(face: freetype.Face, ch: str, pad: int):
    """(sdf_patch, w, h, bearingX, bearingY, advance) — 메트릭은 샘플링 px 기준."""
    face.load_char(ch, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
    g = face.glyph
    m = g.metrics
    metrics = (
        m.width / 64 / SS,
        m.height / 64 / SS,
        m.horiBearingX / 64 / SS,
        m.horiBearingY / 64 / SS,
        m.horiAdvance / 64 / SS,
    )
    bw, bh = g.bitmap.width, g.bitmap.rows
    if bw == 0 or bh == 0:
        return (None,) + metrics
    bitmap = np.array(g.bitmap.buffer, dtype=np.uint8).reshape(bh, bw)
    margin = pad * SS + 2  # SS=2일 때 다운샘플 후 정확히 pad+1
    canvas = np.zeros((bh + margin * 2, bw + margin * 2), dtype=np.uint8)
    canvas[margin : margin + bh, margin : margin + bw] = bitmap
    inside = canvas >= 128
    signed = distance_transform_edt(inside) - distance_transform_edt(~inside)
    sdf = np.clip(0.5 + signed / (2 * pad * SS), 0.0, 1.0)
    h2, w2 = sdf.shape[0] // SS, sdf.shape[1] // SS
    sdf = sdf[: h2 * SS, : w2 * SS].reshape(h2, SS, w2, SS).mean(axis=(1, 3))
    return ((sdf * 255 + 0.5).astype(np.uint8),) + metrics


def build_atlas(
    font_path: Path,
    chars: list[str],
    point: int,
    pad: int,
    width: int,
    height: int,
    face_name: str,
):
    """(atlas ndarray, glyphs, fontInfo) 생성."""
    face = freetype.Face(str(font_path))
    face.set_pixel_sizes(0, point * SS)

    rendered = [(ch,) + render_sdf(face, ch, pad) for ch in chars]
    rendered.sort(key=lambda r: -(r[1].shape[0] if r[1] is not None else 0))

    atlas = np.zeros((height, width), dtype=np.uint8)
    glyphs = []
    x = y = shelf_h = 0
    for ch, patch, w, h, bx, by, adv in rendered:
        if patch is None:
            glyphs.append(
                {
                    "id": ord(ch),
                    "x": 0.0,
                    "y": 0.0,
                    "width": 0.0,
                    "height": 0.0,
                    "xOffset": bx,
                    "yOffset": by,
                    "xAdvance": adv,
                    "scale": 1.0,
                }
            )
            continue
        ph, pw = patch.shape
        if x + pw > width:
            x, y, shelf_h = 0, y + shelf_h, 0
        if y + ph > height:
            raise SystemExit(f"아틀라스 공간 부족 ({face_name}): {ch!r} (y={y})")
        atlas[y : y + ph, x : x + pw] = patch
        margin = pad + 1
        glyphs.append(
            {
                "id": ord(ch),
                "x": float(x + margin),
                "y": float(y + margin),
                "width": w,
                "height": h,
                "xOffset": bx,
                "yOffset": by,
                "xAdvance": adv,
                "scale": 1.0,
            }
        )
        x += pw
        shelf_h = max(shelf_h, ph)

    scale = point / face.units_per_EM
    face.load_char("H", freetype.FT_LOAD_RENDER)
    cap = face.glyph.metrics.horiBearingY / 64 / SS
    ga = next(g["xAdvance"] for g in glyphs if g["width"] > 0)
    info = {
        "Name": face_name,
        "PointSize": float(point),
        "Scale": 1.0,
        "CharacterCount": len(chars),
        "LineHeight": face.size.height / 64 / SS,
        "Baseline": 0.0,
        "Ascender": face.size.ascender / 64 / SS,
        "CapHeight": cap,
        "Descender": face.size.descender / 64 / SS,
        "CenterLine": 0.0,
        "SuperscriptOffset": face.size.ascender / 64 / SS,
        "SubscriptOffset": face.underline_position * scale,
        "SubSize": 0.5,
        "Underline": face.underline_position * scale,
        "UnderlineThickness": face.underline_thickness * scale,
        "strikethrough": cap * 0.4,
        "strikethroughThickness": 0.0,
        "TabWidth": ga * 2.5,
        "Padding": float(pad),
        "AtlasWidth": float(width),
        "AtlasHeight": float(height),
    }
    print(
        f"{face_name}: 글리프 {len(glyphs)}개, {point}px, {width}x{height}, "
        f"높이 사용률 {(y + shelf_h) / height:.0%}"
    )
    return atlas, glyphs, info


def tmp_hash(s: str) -> int:
    """TMP 레거시 TMP_TextUtilities.GetSimpleHashCode."""
    h = 0
    for c in s:
        h = ((h << 5) + h ^ ord(c)) & 0xFFFFFFFF
    return h - 0x100000000 if h >= 0x80000000 else h


def apply_font(
    objects, font_pid, atlas_pid, mat_pid, name, atlas, glyphs, info, fallback_pids=()
):
    font = objects[font_pid]
    tree = font.read_typetree()
    tree["m_Name"] = name
    tree["hashCode"] = tmp_hash(name)
    for key, value in info.items():
        assert key in tree["m_fontInfo"], f"fontInfo에 없는 키 {key}"
        tree["m_fontInfo"][key] = value
    tree["m_glyphInfoList"] = glyphs
    tree["m_kerningInfo"]["kerningPairs"] = []
    tree["fallbackFontAssets"] = [
        {"m_FileID": 0, "m_PathID": pid} for pid in fallback_pids
    ]
    tree["fontCreationSettings"].update(
        fontSourcePath="Pretendard-Regular",
        fontSize=int(info["PointSize"]),
        fontPadding=int(info["Padding"]),
        fontAtlasWidth=int(info["AtlasWidth"]),
        fontAtlasHeight=int(info["AtlasHeight"]),
    )
    font.save_typetree(tree)

    tex = objects[atlas_pid]
    tree = tex.read_typetree()
    tree["m_Name"] = name + " SDF Atlas"
    tree["m_Width"] = int(info["AtlasWidth"])
    tree["m_Height"] = int(info["AtlasHeight"])
    tree["m_TextureFormat"] = 1  # Alpha8
    tree["m_MipCount"] = 1
    data = np.flipud(atlas).tobytes()  # Unity는 아래에서 위로 저장
    tree["m_CompleteImageSize"] = len(data)
    tree["image data"] = data
    if "m_StreamData" in tree:
        tree["m_StreamData"] = {"offset": 0, "size": 0, "path": ""}
    tex.save_typetree(tree)

    mat = objects[mat_pid]
    tree = mat.read_typetree()
    tree["m_Name"] = name + " SDF Material"
    replacements = {
        "_TextureWidth": info["AtlasWidth"],
        "_TextureHeight": info["AtlasHeight"],
        "_GradientScale": info["Padding"] + 1.0,
    }
    tree["m_SavedProperties"]["m_Floats"] = [
        (k, replacements.get(k, v)) for k, v in tree["m_SavedProperties"]["m_Floats"]
    ]
    mat.save_typetree(tree)


def build_bundle(ksp_root: Path, font1, font2) -> None:
    template = ksp_root / "GameData" / "Squad" / "KSPedia" / "kspfonts.ksp"
    if not template.exists():
        raise SystemExit(f"템플릿 없음: {template}")
    env = UnityPy.load(str(template))

    new_cab = "CAB-" + hashlib.md5(b"kspkorean-pretendard-v2").hexdigest()
    renames = {}
    for old in list(env.file.files.keys()):
        if old.startswith("CAB-"):
            suffix = old[old.index(".") :] if "." in old else ""
            renames[old] = new_cab + suffix
    for old, new in renames.items():
        env.file.files[new] = env.file.files.pop(old)

    objects = {obj.path_id: obj for obj in env.objects}

    apply_font(
        objects,
        FONT1_PID,
        ATLAS1_PID,
        MAT1_PID,
        "korean",
        *font1,
        fallback_pids=(FONT2_PID,),
    )
    apply_font(objects, FONT2_PID, ATLAS2_PID, MAT2_PID, "korean2", *font2)

    definition = objects[DEF_PID]
    tree = definition.read_typetree()
    tree["m_Name"] = "korean_bundle"
    tree["m_Script"] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<KSPBundleDefinition xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'UrlName="korean" Name="korean" CreatedTime="0" AutoLoad="false">\n'
        "  <Author />\n  <Info />\n  <Assets>\n"
        '    <Asset Name="korean" Path="Assets/KSPKorean/korean.asset" '
        'Type="TMP_FontAsset" Url="KSPKorean/korean" AutoLoad="false" />\n'
        '    <Asset Name="korean2" Path="Assets/KSPKorean/korean2.asset" '
        'Type="TMP_FontAsset" Url="KSPKorean/korean2" AutoLoad="false" />\n'
        "  </Assets>\n  <Dependencies />\n</KSPBundleDefinition>\n"
    )
    definition.save_typetree(tree)

    bundle = objects[BUNDLE_PID]
    tree = bundle.read_typetree()
    tree["m_Name"] = "korean"
    container = []
    for path, asset_info in tree["m_Container"]:
        pid = asset_info["asset"]["m_PathID"]
        if pid == FONT1_PID:
            path = "assets/kspkorean/korean.asset"
        elif pid == FONT2_PID:
            path = "assets/kspkorean/korean2.asset"
        elif pid == DEF_PID:
            path = "assets/xml/korean_bundle.xml"
        container.append((path, asset_info))
    tree["m_Container"] = container
    bundle.save_typetree(tree)

    # 두 아틀라스 모두 인라인이 되었으므로 스트림 파일(.resS)은 참조가 남지 않으면 제거
    streams_used = False
    for obj in env.objects:
        if obj.type.name == "Texture2D":
            sd = obj.read_typetree().get("m_StreamData")
            if sd and sd.get("path"):
                streams_used = True
    if not streams_used:
        for name in [n for n in env.file.files if n.endswith(".resS")]:
            del env.file.files[name]

    OUT_PATH.write_bytes(env.file.save(packer="lz4"))


def verify() -> None:
    env = UnityPy.load(str(OUT_PATH))
    for obj in env.objects:
        if obj.path_id in (FONT1_PID, FONT2_PID):
            t = obj.read_typetree()
            fi = t["m_fontInfo"]
            print(
                f"검증: {t['m_Name']} 글리프 {len(t['m_glyphInfoList'])}개, "
                f"{fi['PointSize']:.0f}px, {fi['AtlasWidth']:.0f}x{fi['AtlasHeight']:.0f}, "
                f"fallback={t['fallbackFontAssets']}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", required=True, help="Pretendard-Regular.otf 경로")
    parser.add_argument(
        "--ksp", required=True, help="KSP 설치 폴더 (kspfonts.ksp 템플릿용)"
    )
    args = parser.parse_args()
    font_path = Path(args.font)

    common = ksx1001_syllables()
    charset1 = sorted(common) + [chr(c) for c in range(0x3131, 0x3164)]
    charset2 = [chr(c) for c in range(0xAC00, 0xD7A4) if chr(c) not in common]

    font1 = build_atlas(
        font_path,
        charset1,
        point=68,
        pad=8,
        width=4096,
        height=4096,
        face_name="Pretendard",
    )
    font2 = build_atlas(
        font_path,
        charset2,
        point=68,
        pad=8,
        width=8192,
        height=8192,
        face_name="Pretendard Ext",
    )
    build_bundle(Path(args.ksp), font1, font2)
    print(f"저장: {OUT_PATH} ({OUT_PATH.stat().st_size / 1024 / 1024:.1f} MB)")
    verify()
    return 0


if __name__ == "__main__":
    sys.exit(main())
