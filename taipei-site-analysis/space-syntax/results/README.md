# A／B 可達性：來源路網試算

已計算，但不是完整現況模型，也不是 Space Syntax NAIN/NACH。採同一固定南北起訖點，以 Dijkstra 求最短水平投影路徑。

天橋官方存在依據：https://bridge.nco.taipei/bms2/guest/Footbridge/inventory.aspx?vid=64 。源線形為OSM，落點未全部現勘。本輪地面修復含推定幾何，不能外推全段。

{
  "status": "computed_exploratory_source_network",
  "analysis_type": "undirected shortest horizontal route distance, Dijkstra; NOT NAIN/NACH",
  "scope": "北門—台北車站樣區，使用已取得全段OSM線網作背景；外圍資料有限",
  "scenario_time": "平日12:00，Y通道採使用者指定10:30–22:00",
  "radius_type": "network horizontal projected metres",
  "height_cost": "not included: no surveyed z; stair distance is projected proxy",
  "nodes_A": 25503,
  "nodes_B": 25513,
  "edges_A": 27067,
  "edges_B": 27078,
  "components_A": 970,
  "components_B": 970,
  "sample_count": 16,
  "cross_side_pairs": 64,
  "connected_A": 64,
  "connected_B": 64,
  "B_only_pairs": 0,
  "shorter_pairs": 12,
  "radius_counts": {
    "400": {
      "A": 5,
      "B": 8
    },
    "800": {
      "A": 43,
      "B": 44
    },
    "1600": {
      "A": 64,
      "B": 64
    }
  },
  "excluded": {
    "area_boundaries_not_routes": 58,
    "vertical_geometry_not_verified": 292,
    "access_restricted": 53,
    "closed_exit_incident_ways": 4,
    "unverified_internal_level": 28,
    "indoor_access_unverified": 2,
    "stair_endpoint_not_verified": 557
  },
  "limitations": [
    "資料中不連通不等於現地不通",
    "地面修復包含標籤推定巷弄通行、人行道偏移與接點；道路製圖寬度不是實測，詳見ground-repair-audit.json",
    "巷弄採OSM線形，人行道含偏移推定；工區臨時人行道與地下示意圖仍未補接",
    "無三維高程，未套用1:12推定；不宣稱真實步行時間／距離",
    "地下連接尚無逐段核實線形，全部暫不接入；A1封閉出口不接入",
    "B本輪只加入承德市民天橋可追溯線段；尚未完成使用者要求的地下通道模型",
    "天橋存在有官方佐證；OSM樓梯落點尚未全部現勘，結果採其線形條件成立時的試算",
    "半徑與背景邊界效果未充分排除",
    "階梯及電扶梯以雙向步行代理，單向運轉未另建時間模型",
    "抽樣為固定網絡節點，非居民或觀測人流"
  ],
  "ground_repair_segments": 88,
  "ground_repair_report": "ground-repair-audit.json",
  "service_access_continuity_assumed": true
}

CSV空白為來源網絡無路徑，不能解讀為現地不能走。未填補未知高程或直接用示意圖像素量距。A、B圖為同範圍同比例向量圖，橘色是同編號南北樣點路徑，藍色是B新增來源邊。
