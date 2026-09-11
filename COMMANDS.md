# 執行指令與重製方式

本檔保存這次工作的可重製指令；使用專案相對路徑，不包含個人電腦目錄、登入憑證或工作階段日誌。

## 直接閱讀

下載 `urban-history-comparison.html` 後用瀏覽器開啟。圖像、資料、線稿與 JavaScript 均已內嵌，無需安裝套件。

或在本資料夾執行：

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

瀏覽 `http://127.0.0.1:8765/urban-history-comparison.html`。

## 編輯文字、互動與歷史線稿

```sh
python3 -m pip install --target .geo-libs -r requirements.txt
PYTHONPATH=.geo-libs python3 restore_site_assets.py
PYTHONPATH=.geo-libs python3 compose_site_v2.py
PYTHONPATH=.geo-libs python3 build_history_site.py
```

`restore_site_assets.py` 從已交付 HTML 還原內嵌的圖像作為編輯輸入，因此不需要重新下載大批官方資料即可重製頁面。還原的是交付解析度的圖像，並非原始全解析度航照。重製會再編碼圖像，檔案不保證逐位元相同。

- 文字及年代：`build_history_site.py` 的 cases。
- 版面與操作：`site-v2-body.html`、`site-v2.js`（compose_site_v2.py 合成 site-template.html）。
- 歷史判讀線條：`historical/focus-v2.json`，座標基準沿用 traces.json 的 view。
- 產出：`urban-history-comparison.html`、`dist/index.html`、`historical/*.svg`、`historical/*.geojson`。

## 從官方來源重新擷取完整圖資

```sh
PYTHONPATH=.geo-libs python3 fetch_actual.py
PYTHONPATH=.geo-libs python3 fetch_japan_vectors.py
PYTHONPATH=.geo-libs python3 fetch_nyc_vectors.py
PYTHONPATH=.geo-libs python3 fetch_recent_aerials.py
PYTHONPATH=.geo-libs python3 build_actual_plans.py
PYTHONPATH=.geo-libs python3 compose_site_v2.py
PYTHONPATH=.geo-libs python3 build_history_site.py
```

下載可能較久且原始 PDF 較大。官方方案裁圖已內嵌交付 HTML，可先執行 restore_site_assets.py 取得。原始 PDF 來源與節錄頁碼記於 HTML。`build_actual_plans.py` 使用 macOS 中文字型；其他平台需先調整字型路徑。

## 早期示意 3D 工作存檔

`render_models.py`、`compose_boards.py` 與 `source/cities.json` 保留早期示意模型的程式。這些不是實測量體，也不是這次平面階段的最終依據；使用者確認平面前不繼續新增 3D。

## 備份範圍

保存使用者指令、以上執行命令、生成程式、HTML、歷史 SVG／GeoJSON／描圖座標、圖框設定與來源說明。原始大型航照快取、227 MB 官方 PDF、套件資料夾及過期 3D 成品不重複上傳；交付 HTML 已包含閱讀所需圖像。
