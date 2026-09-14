# 市民大道活動圖塊圖

2026-09-14 修訂。A3 橫式、100%原尺寸列印1:5,000；200m比例尺列印長40mm。TWD97 / TM2 121，X/Y等比例。螢幕縮放不改變幾何比例，但不代表螢幕上仍有印刷比例尺。

## 現行圖面

- 以建築／基地圖塊著色，移除所有定位圓點、編號與引線。北側灰綠、南側灰赭；高架藍灰、圖底淺灰。
- 圖層由下至上：設施範圍與地下站體投影、建築及候選建築著色、平面道路雙側線、高架道路；文字另列最上方供閱讀。
- 不繪人行道、步道、階梯中心線。不把建築間留白全認定為人行道。
- 高架依 OSM motorway/trunk 及其連接道的 bridge/layer 標籤辨認；筆畫寬度仍為製圖符號，未取得市民高架完整實測橋面輪廓。停車場高層服務車道不標成市民高架。

## 道路雙側線的證據限制

本版已移除白色道路中心線，以成對外緣表示平面道路。**外緣是推算成果，不是現況實測路緣，亦不是官方道路面向量。**

1. 市府道路面服務的圖層77、78存在，但只開放Map；標準query與identify均回覆不支援。export忽略圖層選擇而回傳含舊設施的完整底圖，已檢視並排除，未用其描現況道路。
2. 改取公開 CA/CIVILMAP_V3/MapServer/3 的道路線與 WIDTH、PWIDTH、MDATE 欄位，原始649筆回覆保存在 official-road-widths.json。這些字段不是當日現地調查。
3. 將有道路名稱的地面 OSM 線段，配對同名、ROADSTRUCT=0、參考頂點距離100m內的最近官方線段。以 WIDTH 欄位按公尺作製圖假設，左右各偏移一半，合併交叉口後只畫外緣。未取得該服務欄位字典；單位及WIDTH究竟對應何種路幅仍需主管機關核對。未使用PWIDTH冒充車道寬。
4. 301個OSM線段配對成功；MDATE包含201003至202401，多數是2010年資料。逐筆來源和輸入寬度列在 road-width-matches.json。缺路寬依據的線段不自行套通用寬度。
5. 固定寬度偏移無法還原轉角、停車彎、實際左右不對稱、中央分隔及改道。圖面可檢查表達方式，不能用來量取現況人行淨寬或車行邊界。完成實際路緣版本仍須新的道路面／路緣圖或定位航照判讀與現勘。

## 活動圖塊的證據限制

設施範圍／建築依OSM實際幾何。中興院區、鐵道部為基地範圍，北門與A1為地下站體投影，台北車站及京站為建築輪廓，不把四者混称同種建物。

後站批發、華陰／太原、長安街口、南陽／許昌的著色，選擇候選街口周邊既有輪廓（面積至少80m²、代表位置距離約106m內），只表示調查選樣。北門郵局選附近建物，入口及建物用途仍需核對。不是逐棟土地使用認定、活動實測範圍或人口密度。選樣建物ID保存在 block-selection.json，不新增圓形或虛構街廓範圍。

## 資料與輸出

- © OpenStreetMap contributors / ODbL：https://www.openstreetmap.org/copyright 。2026-09-14公開Overpass資料，原始來源為 osm-source.json.gz（先前備份）；輪廓缺漏未補畫，不是竣工測繪。
- 官方道路資料：https://arcgis.tpgos.gov.taipei/arcgis/rest/services/CA/CIVILMAP_V3/MapServer/3 。取用參數與限制詳 road-width-source.json。
- activity-map.svg、activity-map.html、activity-map.png；列印PDF位於 output/pdf/taipei-activity-map-a3.pdf。
- SVG中建物／圖塊為向量；道路側線為高解析度透明影像。PDF為高解析度點陣整頁，頁面尺寸已核對A3。
- 重製：Python需Pillow、numpy、reportlab。執行 build_activity_map.py；macOS字型用STHeiti Medium，可換可用繁中字型。所有必需來源已保存，不需再次查網路。

參考圖的製圖技巧與套用方式見 [REFERENCE_TECHNIQUES.md](REFERENCE_TECHNIQUES.md)。調整配色後重新檢查A3尺寸、雙側線、高架層序及無點位標記。
