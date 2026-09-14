# 市民大道基礎設施分圖

先開 `index.html`：三張圖已內嵌，不需網路或伺服器。各張 SVG 可單獨編輯。圖框 1,980 × 1,130 m；420 × 297 mm，100% 列印 1:5,000。列印縮放後請以比例尺判讀。

詳細分析與來源見 `ANALYSIS.md`。本版是桌面診斷，尚非現地測繪或完整土地使用普查。

## 重建

在本專案根目錄，以含 Pillow 的 Python 執行：

```sh
python3 taipei-site-analysis/maps/infrastructure/build_maps.py
python3 taipei-site-analysis/maps/infrastructure/build_page.py
```

依賴本資料夾 `source-geometry.json.gz`，以及上一層既有 `osm-source.json.gz`、`activity-map.svg`、`activity-map-vector.svg`。字型使用 macOS STHeiti；跨系統須換成可用的繁中文字型。

`prepare_geometry.py` 用於重新整理原始 OSM XML。它讀取 `/tmp/site-tile-0.xml` 至 `/tmp/site-tile-3.xml`；不是重建成圖的必要步驟。原始公開查詢為：

- https://api.openstreetmap.org/api/0.6/map?bbox=121.503,25.043,121.514,25.049
- https://api.openstreetmap.org/api/0.6/map?bbox=121.514,25.043,121.524,25.049
- https://api.openstreetmap.org/api/0.6/map?bbox=121.503,25.049,121.514,25.055
- https://api.openstreetmap.org/api/0.6/map?bbox=121.514,25.049,121.524,25.055

2026-09-14 取得。只保存製圖所用 way 的標籤、節點編號及完整幾何，去除使用者帳號等無關編輯資料；不是所有 OSM 圖徵的完整備份。原始請求會帶入與圖幅相交但延伸至圖幅外的完整圖形，成圖依同一框裁切。多重面 relation 尚未完整重建。

`mapped-features.json` 列出參與檢查的圖徵與商圈選取規則。公園面積欄為未裁切 OSM 多邊形幾何面積，非官方核定面積、植被面積或圖框內總綠地；例如玉泉幾何約18,031 m²，與官方2020年面積19,265 m²不同，不混用。

P017 圖表由既有 `../../data/P017-pedestrians-20250625.csv` 產生。不同晚間時窗不得加總，沒有離峰資料，不測試「人主動避開」。

已驗證 SVG 無內嵌點陣 `<image>`，並以 PNG 逐張目視檢查圖層與標籤。純向量不等於提高來源幾何的測量精度。
