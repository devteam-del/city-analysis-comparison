# 等權重路徑重複率

路段比例＝經過該段的不同南北OD路徑數／共同選定OD組數。A/B相同節點及分母；不加入人流權重。不同樓層分開，同一OD重複經過同段只計一次。

活動節點已改為selected-od-inputs.json內的交通、商業及善導寺選項；fixed-sample-points.json現在保存其地面附著結果，已非原16個樣點。原16點僅保留在歷史檔。

本輪132個物理OD，南北配對3,200組，A/B各1,863組有路徑。未接通組仍納入共同分母，另列缺口。每條路徑權重1，藍低紅高且A/B共用色階；灰色代表此樣本沒有通過，非無行人。模型非完整地下網，非人流預測或標準Space Syntax choice。

目前明細：results/route-overlap-rates.json；來源限制：results/REPLACEMENT_REPORT.md。
