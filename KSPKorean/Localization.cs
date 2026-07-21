using KSP.Localization;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using TMPro;
using UnityEngine;

namespace KSPKorean
{
    // 게임에 비내장 언어 'ko'를 등록하고 시작 즉시 전환한다.
    // 참고 구현: https://github.com/BeardVis/KSP-Ukrainian-Localization
    [KSPAddon(KSPAddon.Startup.Instantly, false)]
    public class Localization : MonoBehaviour
    {
        public void Awake()
        {
            if (!Application.isPlaying)
            {
                return;
            }

            // 내장 NotoSansCJK-K 아틀라스에는 호환 자모(ㄱ, ㅏ 등)가 없어 IME 조합 중
            // 낱자가 깨진다. Pretendard 번들(korean.fnt)의 2단 폰트를 언어 폰트로 등록한다:
            //   korean  — KS X 1001 완성형 + 자모 (68px, 상용 텍스트)
            //   korean2 — 나머지 음절 8,822자 (44px, 뷁 같은 희귀 음절)
            FontLoader fontLoader = FindObjectOfType<FontLoader>();
            TMP_FontAsset[] fonts = LoadKoreanFonts(fontLoader);
            if (fontLoader != null && fonts.Length > 0)
            {
                fontLoader.AddGameSubFont("ko", false, fonts);
                fontLoader.AddMenuSubFont("ko", false, fonts);
                fontLoader.SwitchFontLanguage("ko");
                Debug.Log("[KSPKorean] Pretendard fonts registered (" + fonts.Length + ")");
            }
            else
            {
                Debug.Log("[KSPKorean] korean font bundle not available, falling back to stock fonts");
            }

            Localizer.SwitchToLanguage("ko");
        }

        private static TMP_FontAsset[] LoadKoreanFonts(FontLoader fontLoader)
        {
            // FontLoader가 부팅 초기에 GameData의 *.fnt를 자동 로드하므로 보통 여기서 찾는다.
            if (fontLoader != null && fontLoader.LoadedFonts != null)
            {
                TMP_FontAsset[] loaded = FilterKoreanFonts(fontLoader.LoadedFonts);
                if (loaded.Length > 0)
                {
                    return loaded;
                }
            }

            // 방어 경로: 자동 로드가 안 된 경우 번들을 직접 연다.
            string path = Path.Combine(KSPUtil.ApplicationRootPath, "GameData", "KSPKorean", "korean.fnt");
            if (!File.Exists(path))
            {
                return new TMP_FontAsset[0];
            }
            AssetBundle bundle = AssetBundle.LoadFromFile(path);
            if (bundle == null)
            {
                Debug.LogWarning("[KSPKorean] failed to load korean.fnt asset bundle");
                return new TMP_FontAsset[0];
            }
            // 번들은 폰트가 쓰이는 동안 살아 있어야 하므로 Unload하지 않는다.
            return FilterKoreanFonts(bundle.LoadAllAssets<TMP_FontAsset>());
        }

        private static TMP_FontAsset[] FilterKoreanFonts(IEnumerable<TMP_FontAsset> assets)
        {
            return assets
                .Where(asset => asset != null && (asset.name.Equals("korean") || asset.name.Equals("korean2")))
                .OrderBy(asset => asset.name)  // korean(상용) 우선, korean2(희귀) 다음
                .ToArray();
        }
    }
}
