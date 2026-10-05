# 月曜ランチ難民マップ

**月曜ランチ営業**の異国料理寄りレストランを地図にプロットしたウェブアプリです。

## 開き方（おすすめ：そのまま開く）

`index.html` にデータを埋め込み済みです。ブラウザで直接開けます（`file://` 可）。

```bash
# macOS
open /workspace/monday-lunch-map/index.html

# Linux
xdg-open /workspace/monday-lunch-map/index.html
```

または Finder / ファイルマネージャから `index.html` をダブルクリック。

## ローカルサーバーで開く（任意）

```bash
cd /workspace/monday-lunch-map
python3 -m http.server 8765
# ブラウザで http://127.0.0.1:8765/
```

## ファイル

| ファイル | 内容 |
|---------|------|
| `index.html` | アプリ本体（Leaflet、店舗データ＋タイル設定埋め込み） |
| `restaurants.json` | 店舗データ（編集用のコピー） |
| `tiles.json` | 地図タイル設定の単一ソース（禁止ホスト含む） |
| `verify-tiles.py` | 禁止タイル混入チェック＋サンプル取得 |
| `fixtures/` | 過去の失敗例（検証用） |
| `README.md` | この説明 |

## 地図タイルについて

- **使わない:** `tile.openstreetmap.org`（利用ポリシー違反で 403 Access blocked になる）と `basemaps.cartocdn.com`（API キー必須で `file://` が失敗する）。
- **使う:** OpenStreetMap France / HOT の `*.tile.openstreetmap.fr/hot/...`（OSM データ由来・API キー不要。osmfr より速い実測）。設定は `tiles.json` が単一ソースで、実行に必要な項目だけ `index.html` に埋め込まれます。
- **帰属表示:** マップに OpenStreetMap / HOT の attribution を表示します（必須）。

変更後は必ず:

```bash
python3 verify-tiles.py
python3 verify-tiles.py --fixture fixtures/bad-osm.html   # 期待: FAIL（banned host 名入り）→ fixture PASS
python3 verify-tiles.py --fixture fixtures/bad-carto.html # 期待: FAIL（banned host 名入り）→ fixture PASS
```

## 機能

- 店舗ピン（オレンジ）
- ピン／一覧クリックで店名・ジャンル・月曜ランチ時間・予約可否・一言・公式／情報源リンク
- ジャンルチップフィルタ、予約可のみトグル
- モバイル対応

## 注意

- 営業時間・定休日は調査時点の公開情報に基づきます。当日は店舗の最新情報を確認してください。
