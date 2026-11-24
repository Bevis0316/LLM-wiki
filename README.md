# 3D 渲染管線與現代表示法 — LLM Wiki 教學簡報專案

本專案以 Andrej Karpathy「LLM Wiki」三層架構為基礎，先建立可追溯、可更新的中文知識庫，再透過具檢查迴圈（Loop / Graph）的流程產出教學型 HTML 簡報。

## 資料夾架構

```text
llm-wiki-3d-rendering/
├── AGENTS.md                   # Wiki 匯入與簡報驗證規範
├── README.md                   # 本說明文件
├── 00_控制台/
│   └── 首頁.md                  # Obsidian 知識庫入口
├── 01_原始資料/                 # 唯讀區：請放入 5 篇以上原始資料
├── 02_Wiki/                    # AI 編譯出的概念頁（雙向連結）
├── 03_探索/                     # 簡報大綱、草稿、檢查紀錄、流程圖
├── 04_維護/
│   ├── index.md                # 全站頁面索引
│   └── log.md                  # 執行與檢查歷程
├── scripts/
│   └── check_wiki.py           # 自動化檢查腳本（驗證來源追溯與連結）
└── docs/
    ├── index.html              # 教學型 HTML 簡報主程式（可直接開啟或部署 GitHub Pages）
    └── slides-data.js          # 簡報內容資料檔（由 03_探索/簡報草稿.md 轉換）
```

## 快速開始

1. **放入原始資料**：將 5 篇原始文章存成 `.md` 放進 `01_原始資料/`（格式見該資料夾內說明）。
2. **執行 Phase A（建立 Wiki）**：請 AI 嚴格依照 `AGENTS.md` 逐篇匯入至 `02_Wiki/`，並更新 `04_維護/index.md` 與 `log.md`。
3. **執行自動化檢查**：
   ```bash
   python scripts/check_wiki.py
   ```
4. **執行 Phase B（產出簡報）**：先完成 `03_探索/簡報大綱與對應表.md` 與 `簡報草稿.md`，通過檢查後再更新 `docs/slides-data.js`。
5. **瀏覽簡報**：直接雙擊開啟 `docs/index.html`（支援離線瀏覽與鍵盤左右鍵切換），或推送至 GitHub 後開啟 **Settings → Pages → Deploy from `main` / `/docs`**。
