# 市民大道全段純圖塊版

2026-09-15。依使用者要求，圖面與顯示頁不放可見文字、註解、圖例或點位標記。三張圖依序為公園綠地、交通、商業。

## 範圍與比例

- 市民大道一至八段，至南港研究院路；保留既有環河端銜接。
- 三圖共用 EPSG:3826 投影，以 121.56°E、25.049°N 為中心，東西 12,000 m、南北 2,400 m。
- SVG 原尺寸 1,200 × 240 mm，原尺寸列印 1:10,000。畫面顯示或縮放列印不保證該比例。
- 地理查詢範圍 121.501–121.623°E、25.037–25.061°N，圖面採同一矩形裁切。這是比較圖幅，不是步行服務圈或基地界線。
- [交通局市民大道五至六段貫通說明](https://bote.gov.taipei/News_Content.aspx?n=512804BC5B3D57B0&s=EAF46F7C39C31E8B&sms=72544237BBE4C5F6)：2012 年資料，用以核對六至八段延伸至研究院路的走廊範圍，不作現況交通量。

## 圖塊與來源

© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)，ODbL。2026-09-15 取得公開 API /api/0.6/map 與 https://overpass.kumi.systems/api/interpreter 幾何。原始整理結果存於 geometry.json.gz；保存製圖標籤與幾何，不保存不需要的編輯者帳號。

- 淺灰：已取得的地上建築輪廓。沒有建物不代表空地，未標記的用途不代表不存在。
- 綠地圖：OSM leisure=park/garden 與 landuse=grass 等面；公園範圍不等於植被覆蓋。名稱含「廣場」的 way 不作整塊公園著色。公園 relation 只繪可閉合邊界，保留內洞，缺失鏈不強行閉合。
- 交通圖：地上車站／交通建築為藍灰，地下或設施範圍為淺藍。這不是完整公車站、出入口與地下步行網絡圖。
- 商業圖：棕色依 OSM building=commercial/retail/office/supermarket 或 shop 標籤；淡棕依 landuse=commercial/retail 範圍。包含辦公與商業所在建築，不代表所有樓層是零售。全段採一致可用標籤，不沿用前版西段的鄰街候選建物選取法。不是完整逐戶營業普查或法定商業區圖。

## 白色路面與高架

所有平面道路由線位推算成完整白色面，無可見中心線或未填色內部。幾何使用有界轉角的偏移多邊形。

本版 6,280 條可繪製地面道路 way 中，61 條採 OSM width、362 條採可匹配舊 WIDTH、5,857 條採製圖類別寬度；way 數不是街道數。

路寬優先採 OSM width；西段有可匹配的臺北市歷史 WIDTH 資料時採該資料。其餘採道路類別的製圖寬度，寬度來源逐路記錄於 road-width-basis.json.gz。**此版本是設施分布圖，白色面不是實測路緣或已驗證車道範圍；不可據此量車道容量、路權或人行淨寬。** 歷史 WIDTH 來源與限制見上層既有 README。

高架藍灰面最後繪製，壓在其他地理圖層上；寬度採示意值。人行道不另畫線，圖塊間留白不等於已確認可步行空間。

## 檔案

- index.html、01-green.svg、02-transport.svg、03-commerce.svg：純圖塊顯示頁及向量。
- 三張 PNG 與 overview.png：預覽。
- build_full.py：使用已備份幾何重建圖面，Python + Pillow；原有 official-road-widths.json 位於 maps 目錄。
- 上層 infrastructure/index.html 同步指向本版三張圖；舊圖與前輪分析保留供追溯，其診斷範圍仍是原西段，未改寫成全段結論。
