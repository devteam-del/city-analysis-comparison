# 歷史與現況描圖 v2

目前使用 `focus-v2.json` 及 `*_focus_before.svg`／`*_focus_after.svg`。每案使用同一重點視窗，變更標記在 `focus-v2.json` 的 changes 中，標記是比較位置，不是工程界線。

歷史 v2 補畫可辨識的屋頂、路面與地表，尚待判讀部分用斜線遮罩呈現。全區逐棟歷史測繪尚未完成。現況由官方向量裁切，歷史屋頂投影與現況建物足跡並非相同測量方法，不宜直接計算差集。

原 `traces.json` 與沒有 focus 的 SVG／GeoJSON 為 v1 存檔，含已被修正的 Cross-Bronx 河流判讀；僅供版本回溯，正式頁面主圖不再使用。

# 歷史航照判讀線稿 v1

此版本新增三案歷史線稿，已嵌入 ../urban-history-comparison.html。

- 日本橋 1974–1978：12 個選定屋頂、4 段高架路緣。
- Cross-Bronx 1996：10 個選定屋頂、7 段道路邊緣、2 段低可信度河岸。
- West Side 1951：17 個選定屋頂、2 段高架路緣。

traces.json 儲存人工判讀的影像平面座標，view 為判讀預覽大小。GeoJSON 轉換為 WGS84；SVG 為同範圍編輯線稿。資料來自 ../actual-data 中的官方歷史航照，並非借用現況建物。執行 ../build_history_site.py 可重新產生所有線稿與單一 HTML。

描繪可辨識的路面邊緣與主要屋頂投影，不代表完整歷史建物足跡。未逐棟描繪、未作地面控制點校正、未驗證測量精度。高架與樹冠下的遮蔽不能靠影像確定；河岸低可信度段為虛線，其他遮蔽處不補造。1951 年影像有拼接縫，屋頂透視偏移也會影響定位。不能據此計算拆除建物數量或作工程放樣。

日本歷史來源：國土地理院 gazo1，https://maps.gsi.go.jp/development/ichiran.html 。
紐約歷史來源：NYC 1951／1996 航照，https://github.com/CityOfNewYork/nyc-geo-metadata/blob/main/Metadata/Metadata_AerialImagery.md 。
本次人工重繪：2026-09-11。所有圖資年代、計畫來源與比較詮釋詳見 HTML 末尾說明。
