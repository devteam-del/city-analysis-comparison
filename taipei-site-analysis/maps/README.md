# 實際比例候選活動點圖

2026-09-14。A3 橫式，100% 原尺寸列印為 1:5,000。螢幕縮放請讀200m比例尺。

- 平面投影：TWD97 / TM2 121，GRS80。X/Y 使用相同 0.8 SVG 單位／公尺；SVG 4 單位＝1mm。因此200m＝40mm。
- OSM道路與建物：2026-09-14 由 https://overpass.kumi.systems/api/interpreter 取得。© OpenStreetMap contributors，ODbL https://www.openstreetmap.org/copyright 。原始輸出篩除關係元素後壓縮保存為 osm-source.json.gz；不是官方竣工圖，不保證輪廓齊全或每棟皆為當日狀態。
- 道路畫的是實際中心線，筆畫寬度是符號，不表示道路實測寬度。剔除標為地下的建築與步行線。底圖不含完整地下街網絡；未猜畫 Y 區通道或人流箭頭。
- 11個候選點（北門站與園區分開）連結前稿 ACTIVITY_NODES.md；點位由 OSM 地標、街口共用節點或範圍中心取得，詳 activity-nodes.json。不是已觀測人潮、入口測繪或居民居所。
- 醫院／園區外框是地標用地範圍；京站／轉運站與台北車站著色使用建築輪廓。建築資料缺漏處未補畫。機捷點是車站代表位置，不是指定出口。
- 輸出：activity-map.svg（向量）、activity-map.html（離線預覽）、activity-map.png、output/pdf/taipei-activity-map-a3.pdf（A3列印）。PDF內圖為高解析度點陣，向量編輯請用SVG。
- 重製：Python需 Pillow、reportlab；執行 build_activity_map.py，使用本資料夾壓縮圖資；目前字型路徑為macOS STHeiti Medium，可換本機繁中文字型。
- 圖面未定位特定量測入口，下一步需现场確認合法通道、現況施工及出口位置。

## 圖面修訂

依使用者要求刪除人行道、步道、階梯、行人專用道及自行車道線條，以建築間留白閱讀步行空間。留白仍可能包含車道、空地或私人退縮，不能視為已核實的公共人行道邊界或淨寬。未捏造街廓外緣多邊形。
