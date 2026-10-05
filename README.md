# ランチ難民マップ

神田エリアの**異国料理寄り**ランチ候補を地図にプロットしたウェブアプリです。月曜 / 水曜 / 金曜 / 土日で切り替え、その日にランチ営業が確認できた店だけを表示します。

公開サイト: https://monday-lunch-kanda-6116.netlify.app/

## 開き方

`index.html` にデータを埋め込み済みです。ブラウザで直接開けます（`file://` 可）。

```bash
# macOS
open index.html

# Linux
xdg-open index.html
```

または:

```bash
python3 -m http.server 8765
# http://127.0.0.1:8765/
```

## ファイル

| ファイル | 内容 |
|---------|------|
| `index.html` | アプリ本体（Leaflet、店舗データ＋タイル設定埋め込み） |
| `restaurants.json` | 店舗データ（編集用のコピー） |
| `tiles.json` | 地図タイル設定の単一ソース |
| `verify-tiles.py` | 禁止タイル混入チェック＋サンプル取得 |
| `fixtures/` | 過去の失敗例（検証用） |
| `README.md` | この説明 |

## データモデル（曜日ランチ）

各店は `lunchHoursByDay` を持ちます。キーは `mon` / `wed` / `fri` / `sat` / `sun`。

- 公開情報でその日のランチが確認できたときだけキーを入れます（未確認の日はキー省略 → その曜日モードでは非表示）。
- **土日モード:** `sat` または `sun` のどちらかがあれば表示。両方ある場合はカード／ポップアップに `土 … / 日 …` と並べて出します（同じ文字列なら1回だけ）。

営業時間は公式・Tabelog・Hotpepper 等の公開情報を調査した結果です。推測では埋めません。

## 地図タイル

- **使わない:** `tile.openstreetmap.org`、`basemaps.cartocdn.com`
- **使う:** OpenStreetMap France / HOT（`*.tile.openstreetmap.fr/hot/...`）。設定は `tiles.json`。

```bash
python3 verify-tiles.py
python3 verify-tiles.py --fixture fixtures/bad-osm.html   # 期待: FAIL → fixture PASS
python3 verify-tiles.py --fixture fixtures/bad-carto.html # 期待: FAIL → fixture PASS
```

## 機能

- 曜日スイッチ（月曜 / 水曜 / 金曜 / 土日）
- 店舗ピン、ジャンルチップ、予約可のみトグル
- その日のランチ時間・一言・公式／情報源リンク
- マップは表示中の店だけに fitBounds
- モバイル対応

## プライバシー

公開ページには個人の起点住所・徒歩分数・自宅座標は含めません。

## 注意

- 営業時間・定休日は調査時点の公開情報です。当日は店舗の最新情報を確認してください。
- 不定休の店はチップにその旨を書いています。
