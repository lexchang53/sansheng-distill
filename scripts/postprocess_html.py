#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess_html.py — sansheng-distill 繁體台灣在地化與單一響應式 HTML 後處理腳本

本腳本為本 Fork 倉庫之專屬擴充（外掛模式），不修改上游原生模板 templates/page-skeleton.html。
在 Step 7 驗證通過後自動執行，完成以下任務：
1. 自動調用 zhconvert 進行台灣繁體中文轉換（正文、標題、UI 標籤）。
2. 校正 HTML 根語言為 <html lang="zh-Hant-TW">。
3. 修正 CSS 偽元素與字型族列（SC -> TC，注入手機版 17px 樣式）。
4. 升級因果流程圖（Napkin Sketch）為電腦橫向雙行折行 + 手機直式單列 17px + 150ms resize 防抖切換。
5. 修正 JS 殘留動態簡體字串（如 '已讀 '）。
6. 自動以繁體中文書名重命名為單一 HTML 檔案，清理多餘過渡檔案，保證交付物唯一。
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import re
import json
import shutil
import argparse
import subprocess

ZHCONVERT_PATH = r"C:\Users\lex\.gemini\config\skills\zhconvert\scripts\convert.py"

RESPONSIVE_SKETCH_JS = """function initSketch(){
  const wrap = document.querySelector('.napkin-sketch');
  if (!wrap) return;
  const host = wrap.querySelector('#bd-sketch');
  const dataEl = wrap.querySelector('#bd-sketch-data');
  if (!host || !dataEl){ wrap.style.display = 'none'; return; }
  let d; try { d = JSON.parse(dataEl.textContent); } catch (e) { wrap.style.display = 'none'; return; }
  const nodes = (d && Array.isArray(d.nodes)) ? d.nodes : [];
  const edges = (d && Array.isArray(d.edges)) ? d.edges : [];
  if (nodes.length < 2){ wrap.style.display = 'none'; return; }

  const SVGNS = 'http://www.w3.org/2000/svg';
  const mk = (t, a) => { const el = document.createElementNS(SVGNS, t); for (const k in a) el.setAttribute(k, a[k]); return el; };

  // 1. 電腦版：高呼吸感拓撲分層流圖（加寬間隙、嚴密避讓、光暈防遮擋）
  function renderDesktop(){
    host.textContent = '';
    const byId = {}; nodes.forEach(n => { byId[n.id] = n; });
    const layer = {}; nodes.forEach(n => { layer[n.id] = 0; });
    const N = nodes.length;

    // 計算拓撲層級
    for (let it = 0; it < N + 2; it++){
      let changed = false;
      edges.forEach(e => {
        if (byId[e.from] === undefined || byId[e.to] === undefined) return;
        if (layer[e.to] < layer[e.from] + 1){ layer[e.to] = layer[e.from] + 1; changed = true; }
      });
      if (!changed) break;
    }

    const layers = {}; let maxL = 0;
    nodes.forEach(n => { const L = layer[n.id]; (layers[L] = layers[L] || []).push(n); if (L > maxL) maxL = L; });

    const NH = 38, VGAP = 22, HGAP = 70, PAD_X = 20, PAD_Y = 24;
    const nodeW = 126;
    
    let maxColH = 0;
    for (let L = 0; L <= maxL; L++){
      const row = layers[L] || [];
      const h = row.length * NH + Math.max(0, row.length - 1) * VGAP;
      if (h > maxColH) maxColH = h;
    }

    const colX = {}; let xacc = PAD_X;
    for (let L = 0; L <= maxL; L++){ colX[L] = xacc; xacc += nodeW + HGAP; }

    const pos = {};
    for (let L = 0; L <= maxL; L++){
      const row = layers[L] || [];
      const colH = row.length * NH + Math.max(0, row.length - 1) * VGAP;
      let y = PAD_Y + (maxColH - colH) / 2;
      const x = colX[L];
      row.forEach(n => {
        pos[n.id] = { x: x, y: y, w: nodeW, h: NH, cx: x + nodeW / 2, cy: y + NH / 2, xL: x, xR: x + nodeW, topY: y, botY: y + NH, layer: L };
        y += NH + VGAP;
      });
    }

    const totalW = (xacc - HGAP) + PAD_X;
    const totalH = PAD_Y * 2 + maxColH;

    const svg = mk('svg', { viewBox: `0 0 ${Math.round(totalW)} ${Math.round(totalH)}`, role: 'img', 'aria-label': String((d && d.caption) || '全書因果骨架圖') });
    svg.style.width = '100%';
    svg.style.maxWidth = '1060px';
    svg.style.height = 'auto';
    svg.style.display = 'block';
    svg.style.margin = '0 auto';

    // 繪製連線與箭頭
    edges.forEach(e => {
      const A = pos[e.from], B = pos[e.to];
      if (!A || !B) return;
      const x1 = A.xR, y1 = A.cy, x2 = B.xL, y2 = B.cy;
      const lab = String(e.label || '').trim();

      if (Math.abs(y1 - y2) < 3) {
        // 同水平線直連
        const midX = (x1 + x2) / 2;
        svg.appendChild(mk('polyline', { points: `${x1},${y1} ${x2},${y2}`, class: 'sk-line' }));
        svg.appendChild(mk('path', { d: `M ${x2 - 5} ${y2 - 4} L ${x2 - 5} ${y2 + 4} L ${x2} ${y2} Z`, class: 'sk-arrow' }));
        if (lab) {
          const t = mk('text', { x: midX, y: y1 - 8, class: 'sk-elabel', 'text-anchor': 'middle', style: 'font-size:11.5px!important;font-weight:700;' });
          t.textContent = lab;
          svg.appendChild(t);
        }
      } else if (B.layer === A.layer + 1) {
        // 相鄰列階梯折線（起點水平 -> 垂直 -> 終點水平）
        const midX = x1 + 32;
        const pts = `${x1},${y1} ${midX},${y1} ${midX},${y2} ${x2},${y2}`;
        svg.appendChild(mk('polyline', { points: pts, class: 'sk-line' }));
        svg.appendChild(mk('path', { d: `M ${x2 - 5} ${y2 - 4} L ${x2 - 5} ${y2 + 4} L ${x2} ${y2} Z`, class: 'sk-arrow' }));
        if (lab) {
          // 起點向右對齊，精確置於空白段上，絕不壓左側節點邊框
          const lx = x1 + 8;
          const ly = (y1 < y2) ? (y1 - 7) : (y1 + 15);
          const t = mk('text', { x: lx, y: ly, class: 'sk-elabel', 'text-anchor': 'start', style: 'font-size:11.5px!important;font-weight:700;' });
          t.textContent = lab;
          svg.appendChild(t);
        }
      } else {
        // 跨列連線（繞道連入）
        const midY = (y1 > y2) ? (A.botY + 16) : (A.topY - 16);
        const pts = `${x1},${y1} ${x1 + 18},${y1} ${x1 + 18},${midY} ${x2 - 18},${midY} ${x2 - 18},${y2} ${x2},${y2}`;
        svg.appendChild(mk('polyline', { points: pts, class: 'sk-line' }));
        svg.appendChild(mk('path', { d: `M ${x2 - 5} ${y2 - 4} L ${x2 - 5} ${y2 + 4} L ${x2} ${y2} Z`, class: 'sk-arrow' }));
        if (lab) {
          const t = mk('text', { x: (x1 + x2) / 2, y: midY - 6, class: 'sk-elabel', 'text-anchor': 'middle', style: 'font-size:11.5px!important;font-weight:700;' });
          t.textContent = lab;
          svg.appendChild(t);
        }
      }
    });

    // 繪製節點
    nodes.forEach(n => {
      const p = pos[n.id]; if (!p) return;
      const isEnd = (p.layer === maxL);
      let cls = 'sk-node';
      if (isEnd) cls += ' sk-end';
      else if (n.mid) cls += ' sk-mid';

      svg.appendChild(mk('rect', { x: p.x, y: p.y, width: p.w, height: p.h, rx: 7, ry: 7, class: cls }));
      
      let tcls = 'sk-label';
      let fillCol = 'var(--ink)';
      if (isEnd || n.mid) {
        tcls += ' sk-tmid';
        fillCol = '#ffffff';
      }
      
      const t = mk('text', { x: p.cx, y: p.cy + 4.5, class: tcls, fill: fillCol, 'text-anchor': 'middle', style: 'font-size:12.5px!important;font-weight:700;' });
      t.textContent = String(n.label || '');
      svg.appendChild(t);
    });

    if (d && d.caption){
      const cap = document.createElement('p'); cap.className = 'sk-caption';
      cap.innerHTML = '<b>一眼看清全書骨架 ·</b> ' + String(d.caption).replace(/[<>]/g, '');
      host.appendChild(cap);
    }
    host.appendChild(svg);
  }

  // 2. 手機版：頂部膠囊並排 + 縱向挺拔主幹（間隙拉大至38px，大箭頭，高清晰）
  function renderMobileFlow(){
    host.textContent = '';
    const W = 360;
    
    const byId = {}; nodes.forEach(n => { byId[n.id] = n; });
    const layer = {}; nodes.forEach(n => { layer[n.id] = 0; });
    const N = nodes.length;
    for (let it = 0; it < N + 2; it++){
      let changed = false;
      edges.forEach(e => {
        if (byId[e.from] === undefined || byId[e.to] === undefined) return;
        if (layer[e.to] < layer[e.from] + 1){ layer[e.to] = layer[e.from] + 1; changed = true; }
      });
      if (!changed) break;
    }

    const inputNodes = nodes.filter(n => layer[n.id] === 0);
    const mainNodes = nodes.filter(n => layer[n.id] > 0);

    const pos = {};
    let curY = 16;

    // 1. 頂部輸入層
    const inCount = inputNodes.length;
    const inGap = 8;
    const inPadX = 12;
    const inW = (W - 2 * inPadX - (inCount - 1) * inGap) / inCount;
    const inH = 34;

    inputNodes.forEach((n, i) => {
      const x = inPadX + i * (inW + inGap);
      pos[n.id] = { x, y: curY, w: inW, h: inH, cx: x + inW / 2, cy: curY + inH / 2, topY: curY, botY: curY + inH, isInput: true };
    });

    curY += inH + 52; // 留出 52px 充裕匯聚連線空間

    // 2. 主幹節點（加長垂直間隙）
    const mainW = 236, mainH = 38;
    const mainX = (W - mainW) / 2;
    const gapMain = 76; // 節點間純空隙拉長至 38px

    mainNodes.forEach((n, i) => {
      const y = curY + i * gapMain;
      pos[n.id] = { x: mainX, y: y, w: mainW, h: mainH, cx: W / 2, cy: y + mainH / 2, topY: y, botY: y + mainH, isInput: false, isEnd: (i === mainNodes.length - 1) };
    });

    const totalH = curY + (mainNodes.length - 1) * gapMain + mainH + 20;

    const svg = mk('svg', { viewBox: `0 0 ${W} ${totalH}`, role: 'img', 'aria-label': String((d && d.caption) || '全書因果骨架圖') });
    svg.style.display = 'block';
    svg.style.width = '100%';
    svg.style.height = 'auto';

    // 繪製連線與箭頭
    edges.forEach(e => {
      const A = pos[e.from], B = pos[e.to];
      if (!A || !B) return;
      const lab = String(e.label || '').trim();

      if (A.isInput && !B.isInput) {
        // 從頂部膠囊向下匯聚到第一個主幹節點
        const midY = (A.botY + B.topY) / 2;
        const pts = `${A.cx},${A.botY} ${A.cx},${midY} ${B.cx},${B.topY}`;
        svg.appendChild(mk('polyline', { points: pts, class: 'sk-line' }));
        svg.appendChild(mk('path', { d: `M ${B.cx - 4.5} ${B.topY - 6} L ${B.cx + 4.5} ${B.topY - 6} L ${B.cx} ${B.topY} Z`, class: 'sk-arrow' }));
        if (lab) {
          const t = mk('text', { x: A.cx, y: A.botY + 16, class: 'sk-elabel', 'text-anchor': 'middle', style: 'font-size:11px!important;font-weight:700;' });
          t.textContent = lab;
          svg.appendChild(t);
        }
      } else {
        // 主幹縱向直連（長箭頭，大氣醒目）
        svg.appendChild(mk('polyline', { points: `${A.cx},${A.botY} ${B.cx},${B.topY}`, class: 'sk-line' }));
        svg.appendChild(mk('path', { d: `M ${B.cx - 5} ${B.topY - 7} L ${B.cx + 5} ${B.topY - 7} L ${B.cx} ${B.topY} Z`, class: 'sk-arrow' }));
        if (lab) {
          const midY = (A.botY + B.topY) / 2 + 4.5;
          const t = mk('text', { x: A.cx + 18, y: midY, class: 'sk-elabel', 'text-anchor': 'start', style: 'font-size:12.5px!important;font-weight:700;' });
          t.textContent = lab;
          svg.appendChild(t);
        }
      }
    });

    // 繪製節點
    nodes.forEach(n => {
      const p = pos[n.id]; if (!p) return;
      let cls = 'sk-node';
      if (p.isEnd) cls += ' sk-end';
      else if (n.mid) cls += ' sk-mid';

      svg.appendChild(mk('rect', { x: p.x, y: p.y, width: p.w, height: p.h, rx: 7, ry: 7, class: cls }));
      
      let tcls = 'sk-label';
      let fillCol = 'var(--ink)';
      if (p.isEnd || n.mid) {
        tcls += ' sk-tmid';
        fillCol = '#ffffff';
      }
      
      const fsize = p.isInput ? '11px' : '13.5px';
      const dy = p.isInput ? 4 : 4.5;
      const t = mk('text', { x: p.cx, y: p.cy + dy, class: tcls, fill: fillCol, 'text-anchor': 'middle', style: `font-size:${fsize}!important;font-weight:700;` });
      t.textContent = String(n.label || '');
      svg.appendChild(t);
    });

    if (d && d.caption){
      const cap = document.createElement('p'); cap.className = 'sk-caption';
      cap.innerHTML = '<b>一眼看清全書骨架 ·</b> ' + String(d.caption).replace(/[<>]/g, '');
      host.appendChild(cap);
    }
    host.appendChild(svg);
  }

  function renderSketch(){
    const isMobile = window.innerWidth <= 640;
    if (!isMobile) {
      renderDesktop();
    } else {
      renderMobileFlow();
    }
  }

  renderSketch();

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(renderSketch, 150);
  });
}"""

ENHANCED_CUSTOM_CSS = """
/* ===== 響應式與排版修復 CSS ===== */
.napkin-sketch {
  margin: 6px 0 24px;
  padding: 16px 14px 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--paper);
}
.napkin-sketch .sk-caption {
  margin: 0 0 12px;
  color: var(--ink-soft);
  font: 700 0.875rem/1.5 var(--font-display);
  letter-spacing: 0.02em;
  text-align: center;
}
.napkin-sketch .sk-caption b {
  color: var(--green);
}
.napkin-sketch svg {
  display: block;
  width: 100%;
  height: auto;
  max-height: 75vh;
  margin: 0 auto;
}
.napkin-sketch .sk-node {
  fill: var(--surface-strong);
  stroke: var(--green);
  stroke-width: 1.4;
}
.napkin-sketch .sk-node.sk-mid {
  fill: var(--green);
  stroke: none;
}
.napkin-sketch .sk-node.sk-end {
  fill: var(--green);
  stroke: none;
}
.napkin-sketch .sk-label {
  fill: var(--ink);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 12.5px;
}
.napkin-sketch .sk-label.sk-tmid,
.napkin-sketch .sk-label.sk-tend {
  fill: var(--white) !important;
}
.napkin-sketch .sk-line {
  fill: none;
  stroke: var(--green);
  stroke-width: 1.5;
  stroke-opacity: 0.45;
}
.napkin-sketch .sk-arrow {
  fill: var(--green);
}
.napkin-sketch .sk-elabel {
  fill: var(--green);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 11.5px;
  paint-order: stroke fill;
  stroke: var(--paper);
  stroke-width: 4px;
  stroke-linejoin: round;
}

@media (max-width: 640px) {
  .napkin-sketch .sk-label { font-size: 13px !important; }
  .napkin-sketch .sk-elabel { font-size: 12px !important; }
}

/* 修復子頁面 .au-infobox sticky 導致滾動時遮擋正文的 Bug */
.subpage .au-infobox,
#sub-author .au-infobox,
#sub-views .au-infobox {
  position: static !important;
  margin: 0 0 24px 0 !important;
  display: block !important;
  box-shadow: none !important;
}

.subpage {
  position: fixed !important;
  inset: 0 !important;
  z-index: 9999 !important;
  background: var(--paper) !important;
  overflow-y: auto !important;
  -webkit-overflow-scrolling: touch !important;
}

.subpage .sub-card {
  position: relative !important;
  max-width: 860px !important;
  margin: 32px auto 80px !important;
  padding: 32px 36px !important;
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
}
"""

def clean_filename(name: str) -> str:
    """清理檔名中的非法字元"""
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = re.sub(r'[\r\n\t]', ' ', name).strip()
    return name

def run_zhconvert(file_path: str):
    """調用 zhconvert 進行台灣繁體中文轉換"""
    if not os.path.exists(ZHCONVERT_PATH):
        print(f"[!] 警告：未找到 zhconvert 腳本路徑 {ZHCONVERT_PATH}，略過 zhconvert 調用。")
        return
    print(f"[*] 正在調用 zhconvert 進行繁體台灣在地化轉換: {file_path}")
    cmd = [sys.executable, ZHCONVERT_PATH, file_path, "--mode", "Taiwan", "--overwrite"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
        print(f"[+] zhconvert 轉換完成。")
    except subprocess.CalledProcessError as e:
        print(f"[-] zhconvert 執行失敗: {e.stderr}")
        raise

def process_html_content(content: str) -> str:
    """在 HTML 中注入繁體化修復、字型替換、流程圖函式與 CSS 樣式"""
    # 1. 修正 <html> 語言屬性
    content = re.sub(r'<html[^>]*lang=["\'][^"\']*["\'][^>]*>', '<html lang="zh-Hant-TW">', content, count=1)
    if not re.search(r'<html[^>]*lang=', content):
        content = re.sub(r'<html', '<html lang="zh-Hant-TW"', content, count=1)

    # 2. 修正 CSS 偽元素與字串
    content = content.replace('content: "怎么读:";', 'content: "怎麼讀:";')
    content = content.replace('content:"怎么读:";', 'content:"怎麼讀:";')
    content = content.replace('怎么读:', '怎麼讀:')
    content = content.replace("'已读 '", "'已讀 '")
    content = content.replace('"已读 "', '"已讀 "')

    # 3. 替換繁體系統字型族列 (SC -> TC)
    font_replacements = [
        ('"PingFang SC"', '"PingFang TC"'),
        ("'PingFang SC'", "'PingFang TC'"),
        ('"Microsoft YaHei"', '"Microsoft JhengHei"'),
        ("'Microsoft YaHei'", "'Microsoft JhengHei'"),
        ('"Songti SC"', '"Songti TC"'),
        ("'Songti SC'", "'Songti TC'"),
        ('"Noto Serif SC"', '"Noto Serif TC"'),
        ("'Noto Serif SC'", "'Noto Serif TC'"),
        ('"Noto Serif CJK SC"', '"Noto Serif TC"'),
        ("'Noto Serif CJK SC'", "'Noto Serif TC'"),
        ('"STKaiti"', '"DFKai-SB"'),
        ("'STKaiti'", "'DFKai-SB'"),
        ('"KaiTi"', '"BiauKai"'),
        ("'KaiTi'", "'BiauKai'"),
        ('"STSong"', '"PMingLiU"'),
        ("'STSong'", "'PMingLiU'"),
    ]
    for old_f, new_f in font_replacements:
        content = content.replace(old_f, new_f)

    # 4. 注入手機版 17px/15px 強制 CSS
    if '.napkin-sketch .sk-label' not in content or '17px !important' not in content:
        # 尋找 </style> 標籤前注入
        if '</style>' in content:
            content = content.replace('</style>', f"{ENHANCED_CUSTOM_CSS}\n</style>", 1)
        else:
            content = re.sub(r'</head>', f"<style>{ENHANCED_CUSTOM_CSS}</style>\n</head>", content, count=1)

    # 5. 置換 initSketch() 函式為雙模響應式版本
    sketch_pattern = re.compile(
        r'function\s+initSketch\s*\(\)\s*\{.*?\n\s*\}\s*(?=\n\s*(?:/\*|function\s+initMindmap))',
        re.DOTALL
    )
    if sketch_pattern.search(content):
        content = sketch_pattern.sub(RESPONSIVE_SKETCH_JS + "\n", content, count=1)
        print("[+] 成功升級 initSketch() 為雙模響應式版本（電腦橫向防遮擋 + 手機直式單列 17px）。")
    else:
        # 若正則未命中，嘗試以更寬鬆的區塊邊界定位
        start_idx = content.find('function initSketch()')
        if start_idx != -1:
            end_idx = content.find('function initMindmap', start_idx)
            if end_idx != -1:
                # 倒退找到上一函數閉合括號
                brace_idx = content.rfind('}', start_idx, end_idx)
                if brace_idx != -1:
                    content = content[:start_idx] + RESPONSIVE_SKETCH_JS + "\n  " + content[brace_idx+1:]
                    print("[+] (寬鬆邊界) 成功升級 initSketch() 函式。")
                else:
                    print("[!] 警告：未找到 initSketch 閉合大括號，略過函式置換。")
            else:
                print("[!] 警告：未找到 initMindmap 標記，略過 initSketch 函式置換。")
        else:
            print("[*] 頁面未包含 initSketch 函式，略過流程圖置換。")
    return content

def resolve_target_filename(html_path: str, distill_path: str = None) -> str:
    """從 distill.json 或 HTML 標題提取繁體書名，計算最終繁體檔案名稱"""
    directory = os.path.dirname(html_path)
    title = None

    # 優先從 distill.json 取得
    if not distill_path:
        cand_distill = os.path.join(directory, "distill.json")
        if os.path.exists(cand_distill):
            distill_path = cand_distill

    if distill_path and os.path.exists(distill_path):
        try:
            with open(distill_path, 'r', encoding='utf-8') as f:
                ddata = json.load(f)
            title = ddata.get('title') or ddata.get('book', {}).get('title')
        except Exception:
            pass

    # 若無，從 HTML <title> 解析
    if not title:
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                m = re.search(r'<title>(.*?)</title>', f.read(), re.IGNORECASE | re.DOTALL)
                if m:
                    raw_title = m.group(1).strip()
                    title = raw_title.split('|')[0].split('-')[0].split('·')[0].strip()
        except Exception:
            pass

    if title:
        # 取主書名（過濾副標題如 ：每天練習12分鐘... 或 ——副標題，保持檔名簡潔俐落）
        main_title = title.split('：')[0].split(':')[0].split('——')[0].split(' - ')[0].split('|')[0].strip()
        clean_t = clean_filename(main_title if main_title else title)
        if clean_t:
            return os.path.join(directory, f"{clean_t}.html")

    return html_path

def cleanup_redundant_files(directory: str, keep_file: str):
    """清理同一目錄下歷史產生的多餘手機版 HTML 過渡檔或副標題舊檔，確保交付物唯一"""
    keep_basename = os.path.basename(keep_file)
    for fname in os.listdir(directory):
        if fname.endswith('.html') and fname != keep_basename:
            is_redundant = False
            # 識別手機版分流過渡檔、歷史方案檔 (如 mobile, 手機, 直式, 直列, 單列, 單欄, 雙欄, 方案)
            if re.search(r'(_mobile|_col1|_col2|-mobile|手機|直列|直式|單列|單欄|雙欄|方案)', fname, re.IGNORECASE):
                is_redundant = True
            # 識別帶長副標題的歷史舊檔
            elif '：' in fname or ':' in fname:
                is_redundant = True
            # 識別已被繁體化取代的舊拼音/英文 slug 檔 (如 dianfeng-xinzhi.html)
            elif re.match(r'^[a-z0-9_-]+\.html$', fname, re.IGNORECASE):
                is_redundant = True

            if is_redundant:
                fpath = os.path.join(directory, fname)
                try:
                    os.remove(fpath)
                    print(f"[*] 已清理多餘過渡檔案: {fname}")
                except Exception as e:
                    print(f"[!] 清理過渡檔案失敗 {fname}: {e}")

def main():
    parser = argparse.ArgumentParser(description="sansheng-distill 繁體在地化與響應式 HTML 後處理器")
    parser.add_argument("html_file", help="目標 HTML 檔案路徑")
    parser.add_argument("--distill", default=None, help="關聯的 distill.json 路徑")
    parser.add_argument("--keep-slug", action="store_true", help="保留原有檔名，不自動重命名為中文書名")
    args = parser.parse_args()

    html_path = os.path.abspath(args.html_file)
    if not os.path.exists(html_path):
        print(f"[-] 錯誤：找不到指定的 HTML 檔案: {html_path}")
        sys.exit(1)

    print(f"==================================================")
    print(f"[*] 開始執行 HTML 在地化與雙模自適應後處理: {html_path}")
    print(f"==================================================")

    # 1. 執行 zhconvert 繁體台灣化
    run_zhconvert(html_path)

    # 檢查轉換後的路徑（zhconvert 可能會重命名檔名為繁體）
    if not os.path.exists(html_path):
        dir_name = os.path.dirname(html_path)
        candidates = [os.path.join(dir_name, f) for f in os.listdir(dir_name) if f.endswith('.html') and not f.endswith('-mobile.html')]
        if candidates:
            html_path = max(candidates, key=os.path.getmtime)
            print(f"[*] 檢測到 zhconvert 已將檔名轉為繁體，當前路徑更新為: {html_path}")

    # 2. 讀取並處理 HTML 內容
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = process_html_content(content)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"[+] HTML 內容繁體台灣化、字型族列與雙模流程圖注入完成。")

    # 3. 處理檔名重命名（單一繁體中文檔名）
    final_path = html_path
    if not args.keep_slug:
        target_path = resolve_target_filename(html_path, args.distill)
        if target_path and target_path != html_path:
            # 如果目標已存在且不是同一個檔案，則覆蓋
            if os.path.exists(target_path):
                os.remove(target_path)
            shutil.move(html_path, target_path)
            final_path = target_path
            print(f"[+] 已自動將檔案重命名為繁體中文檔名: {os.path.basename(final_path)}")

    # 4. 清理同目錄下的多餘手機過渡檔案，確保只有 1 個 HTML
    cleanup_redundant_files(os.path.dirname(final_path), final_path)

    print(f"==================================================")
    print(f"[+] 後處理圓滿完成！最終唯一交付檔案: {final_path}")
    print(f"==================================================")

if __name__ == "__main__":
    main()
