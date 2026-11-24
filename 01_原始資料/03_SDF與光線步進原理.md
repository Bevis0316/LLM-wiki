---
title: "Further Graphics: Ray Marching and Signed Distance Fields"
source: "[[03_SDF與光線步進原理.pdf]]"
author:
  - "Alex Benton (University of Cambridge)"
created: 2026-11-24
topic_role: "03 數學派表示法（SDF 與光線步進）"
tags:
  - "clippings"
  - "pdf-extract"
---

> 本檔為唯讀原檔 [[03_SDF與光線步進原理.pdf]]（共 23 頁）之核心內容忠實萃取，供 `02_Wiki/` 編譯與追溯頁碼使用。

## 1. GPU 光線追蹤基礎（p.2–p.5）
- 核心概念：透過像素發射光線，依據擊中的物體決定像素顏色（"Let the pixel make up its own mind"）。
- OpenGL 實作方式：只建立最簡幾何（單一四邊形 Quad）與最簡頂點著色器（不做變換），讓 GPU 內插頂點座標到每個像素，將所有光線計算交由片段著色器（Fragment Shader，GLSL）平行執行。
- 解析解範例（p.5）：針對球體可直接以數學公式 `traceSphere` 求光線與球體交點及法線。

## 2. 傳統 Ray-marching（光線步進）與其缺點（p.6）
- 原理：沿著光線方向以固定有限步長逐步前進，直到撞到物體或超過最大步數上限（有時也稱為 ray casting）。
- 優點：場景物體只需回答「光線是否擊中（y/n）」，適合高度場（height fields）等資料。
- 缺點：
  - 通常需要大量步數。
  - 步長太大容易跨過物體而漏掉交點（lost intersections）。
  - 在 `for()` 迴圈核心內做 `if()` 判斷非常不利於 GPU 最佳化。

## 3. Signed Distance Fields（SDF）與 Sphere Tracing（p.7–p.10）
- **SDF 定義（p.8）**：輸入空間中任意一點 p，回傳 p 到物體表面的最小可能距離。正值為外部、零為表面、負值為內部（絕對值仍代表到表面的距離）。
- **Sphere Tracing（球體追蹤，p.7）**：每一步查詢距離場函數 d(p)（到最近物體的距離），沿光線安全前進距離 d，因為最近的交點不可能比 d 更近，大幅提升 GPU 即時效能。
- **常見基本體公式（p.8）**：球體 `length(p) - r`、立方體 `cube`、圓柱 `cylinder`、環面 `torus`。
- **迴圈終止條件（p.9）**：當 `abs(d) <= 0.001`（視為擊中表面）或步數達上限（如 `step < 50`）時停止；步數越多代表光線貼近邊緣掠過（p.10）。

## 4. 組合、融合與變換 SDF（p.11–p.16）
- **布林運算（CSG，p.11–p.12）**：聯集 `min(A, B)`、交集 `max(A, B)`、差集 `max(A, -B)`。
- **平滑融合（Blending，p.13）**：直接取 `min/max` 會產生尖銳不連續接縫；改用多項式平滑函數（如 Inigo Quilez 的 `smin`）內插可實現圓滑有機融合。
- **空間變換（p.14–p.15）**：旋轉、平移或縮放 SDF 模型需對輸入點 `pt` 套用逆變換（inverse transform）。
- **非均勻空間扭曲（p.16）**：可依空間位置動態扭曲座標（如隨 y 軸旋轉產生扭轉方塊）。

## 5. 法線、軟陰影與無限重複（p.17–p.21）
- **求表面法線（p.17）**：利用距離場在表面附近的局部線性特性，以有限差分近似局部梯度（local gradient）求得法線。
- **軟陰影（p.18–p.19）**：朝光源步進時，依據光線掠過障礙物的距離與前進距離比值（如 `min(kd, 16 * d / t)`），幾乎零額外成本即可產生軟陰影。
- **零成本無限重複（p.20–p.21）**：在計算距離前對座標取餘數（`mod`），不需額外記憶體即可生成無限多個幾何體。
