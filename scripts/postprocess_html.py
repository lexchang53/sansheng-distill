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

  // 1. 電腦版：橫向雙行文字無遮擋版
  function renderDesktop(){
    host.textContent = '';
    const FS = 12, PADX = 18, NH = 38, HGAP = 58, PAD = 14;
    const wOf = n => Math.max(122, String(n.label || '').length * 15 + PADX * 2);

    let xacc = PAD;
    const pos = {};
    nodes.forEach(n => {
      const w = wOf(n);
      pos[n.id] = { x: xacc, y: PAD, w: w, h: NH, cx: xacc + w / 2, cy: PAD + NH / 2, xL: xacc, xR: xacc + w };
      xacc += w + HGAP;
    });
    const totalW = xacc - HGAP + PAD;
    const totalH = PAD * 2 + NH;

    const svg = mk('svg', { viewBox: `0 0 ${Math.round(totalW)} ${Math.round(totalH)}`, role: 'img', 'aria-label': String((d && d.caption) || '全書因果骨架圖') });

    // Lines & Arrows
    edges.forEach(e => {
      const A = pos[e.from], B = pos[e.to];
      if (!A || !B) return;
      const x1 = A.xR, y1 = A.cy, x2 = B.xL, y2 = B.cy;
      svg.appendChild(mk('polyline', { points: `${x1},${y1} ${x2},${y2}`, class: 'sk-line' }));
      const ah = 5;
      svg.appendChild(mk('path', { d: `M ${x2 - ah} ${y2 - ah} L ${x2 - ah} ${y2 + ah} L ${x2} ${y2} Z`, class: 'sk-arrow' }));
    });

    // Nodes
    nodes.forEach(n => {
      const p = pos[n.id]; if (!p) return;
      const cls = 'sk-node' + (n.mid ? ' sk-mid' : '');
      svg.appendChild(mk('rect', { x: p.x, y: p.y, width: p.w, height: p.h, rx: 8, ry: 8, class: cls }));
      const tcls = 'sk-label' + (n.mid ? ' sk-tmid' : '');
      const t = mk('text', { x: p.cx, y: p.cy + 4.5, class: tcls, 'text-anchor': 'middle', 'font-size': '12px' });
      t.textContent = String(n.label || '');
      svg.appendChild(t);
    });

    // Edge Labels (Strictly on top of line, 2 lines for >= 4 chars)
    edges.forEach(e => {
      const A = pos[e.from], B = pos[e.to];
      if (!A || !B) return;
      const midX = (A.xR + B.xL) / 2;
      const yLine = A.cy;
      const lab = String(e.label || '').trim();
      if (!lab) return;

      if (lab.length <= 3) {
        const t = mk('text', { x: midX, y: yLine - 8, class: 'sk-elabel', 'text-anchor': 'middle', 'font-size': '11.5px' });
        t.textContent = lab;
        svg.appendChild(t);
      } else {
        const line1 = lab.slice(0, 2);
        const line2 = lab.slice(2);
        const t = mk('text', { x: midX, y: yLine - 16, class: 'sk-elabel', 'text-anchor': 'middle', 'font-size': '11px' });
        const ts1 = mk('tspan', { x: midX, dy: '0' }); ts1.textContent = line1;
        const ts2 = mk('tspan', { x: midX, dy: '12' }); ts2.textContent = line2;
        t.appendChild(ts1);
        t.appendChild(ts2);
        svg.appendChild(t);
      }
    });

    if (d && d.caption){
      const cap = document.createElement('p'); cap.className = 'sk-caption';
      cap.innerHTML = '<b>一眼看清全書骨架 ·</b> ' + String(d.caption).replace(/[<>]/g, '');
      host.appendChild(cap);
    }
    host.appendChild(svg);
  }

  // 2. 手機版：唯一專屬「直式單列版」（字體適度放大，節點 17px，標籤 15px，框高 48px）
  function renderMobileSingleCol(){
    host.textContent = '';
    const W = 350;
    const nodeW = 250, nodeH = 48;
    const yStart = 16, gapY = 82;
    const H = yStart * 2 + (nodes.length - 1) * gapY + nodeH;
    
    const svg = mk('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': String((d && d.caption) || '全書因果骨架圖') });
    svg.style.display = 'block';
    svg.style.width = '100%';
    svg.style.height = 'auto';

    const cX = W / 2;
    const x = (W - nodeW) / 2;

    const pos = {};
    nodes.forEach((n, i) => {
      const y = yStart + i * gapY;
      pos[n.id] = { x: x, y: y, w: nodeW, h: nodeH, cx: cX, cy: y + nodeH / 2, topY: y, botY: y + nodeH };
    });

    // Lines & Arrows
    edges.forEach(e => {
      const A = pos[e.from], B = pos[e.to];
      if (!A || !B) return;
      svg.appendChild(mk('polyline', { points: `${A.cx},${A.botY} ${B.cx},${B.topY}`, class: 'sk-line' }));
      svg.appendChild(mk('path', { d: `M ${B.cx - 5} ${B.topY - 7} L ${B.cx + 5} ${B.topY - 7} L ${B.cx} ${B.topY} Z`, class: 'sk-arrow' }));
      const midY = (A.botY + B.topY) / 2 + 5.5;
      const t = mk('text', { x: A.cx + 20, y: midY, class: 'sk-elabel', 'text-anchor': 'start', style: 'font-size:15px!important;font-weight:700;' });
      t.textContent = String(e.label || '');
      svg.appendChild(t);
    });

    // Nodes (Font size 17px, strictly matching napkin body text)
    nodes.forEach(n => {
      const p = pos[n.id]; if (!p) return;
      const cls = 'sk-node' + (n.mid ? ' sk-mid' : '');
      svg.appendChild(mk('rect', { x: p.x, y: p.y, width: p.w, height: p.h, rx: 9, ry: 9, class: cls }));
      const tcls = 'sk-label' + (n.mid ? ' sk-tmid' : '');
      const fillCol = n.mid ? '#fffaf0' : 'var(--ink)';
      const t = mk('text', { x: p.cx, y: p.cy + 6, class: tcls, fill: fillCol, 'text-anchor': 'middle', style: 'font-size:17px!important;font-weight:700;' });
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
      renderMobileSingleCol();
    }
  }

  renderSketch();

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(renderSketch, 150);
  });
}"""

MOBILE_NAPKIN_CSS = """
@media (max-width: 640px) {
  .napkin-sketch .sk-label { font-size: 17px !important; }
  .napkin-sketch .sk-elabel { font-size: 15px !important; }
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
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
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
            content = content.replace('</style>', f"{MOBILE_NAPKIN_CSS}\n</style>", 1)
        else:
            content = re.sub(r'</head>', f"<style>{MOBILE_NAPKIN_CSS}</style>\n</head>", content, count=1)

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
