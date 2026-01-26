#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pypdf import PdfReader
import zipfile

BASE = "https://www.motie.go.kr"
LIST_URL = f"{BASE}/kor/article/ATCL3f49a5a8c"  # 보도·참고자료 목록(페이지 인덱스)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.7",
    "Connection": "keep-alive",
})

DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
VIEWER_RE = re.compile(r"/attach/viewer/([^/]+)/([^/]+)/([^\"'\s]+)")
# /attach/viewer/{dir}/{filehash}/{viewerhash}

@dataclass
class DocMeta:
    title: str
    date: str
    dept: str
    view_url: str
    download_urls: List[str]  # 후보(대개 PDF/HWPX)

def iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--keyword", default="", help="필터 키워드(본문 또는 제목 포함)")
    ap.add_argument("--out", required=True, help="출력 폴더")
    ap.add_argument("--sleep", type=float, default=0.6, help="요청 간 대기(초)")
    ap.add_argument("--max_pages", type=int, default=200, help="최대 목록 페이지 탐색 수")
    return ap.parse_args()

def get_html(url: str, timeout: int = 30) -> str:
    r = SESSION.get(url, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text

def safe_filename(s: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|]+", "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:120]

def within_range(date_str: str, start: datetime, end: datetime) -> bool:
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return start <= d <= end

def crawl_list(start: datetime, end: datetime, sleep_s: float, max_pages: int) -> List[str]:
    """목록 페이지를 순회하며 기간 내 view 링크를 수집."""
    view_urls = []
    for page in range(1, max_pages + 1):
        url = f"{LIST_URL}?pageIndex={page}"
        html = get_html(url)
        soup = BeautifulSoup(html, "lxml")

        # 목록 테이블/리스트 구조는 변경될 수 있어, 'view' 패턴 링크를 넓게 수집
        links = soup.select("a[href*='/kor/article/ATCL3f49a5a8c/'][href*='/view']")
        if not links:
            # 구조 변경 대비: 전체 링크 스캔
            links = soup.find_all("a", href=True)

        page_has_any = False
        for a in links:
            href = a.get("href", "")
            if "/kor/article/ATCL3f49a5a8c/" in href and "/view" in href:
                title = (a.get_text() or "").strip()
                full = urljoin(BASE, href)
                # 제목 옆에 날짜가 같이 있는 경우가 많으나, 안정성을 위해 view에서 날짜를 최종 판정
                view_urls.append(full)
                page_has_any = True

        # 목록이 더 이상 없으면 종료
        if not page_has_any and page > 3:
            break

        time.sleep(sleep_s)

    # 중복 제거(순서 유지)
    seen = set()
    uniq = []
    for u in view_urls:
        if u not in seen:
            uniq.append(u)
            seen.add(u)
    return uniq

def extract_meta_from_view(view_url: str, sleep_s: float) -> Optional[DocMeta]:
    html = get_html(view_url)
    soup = BeautifulSoup(html, "lxml")

    # 제목
    title = ""
    h = soup.find(["h1", "h2", "h3"])
    if h:
        title = h.get_text(strip=True)
    if not title:
        title = soup.title.get_text(strip=True) if soup.title else view_url

    # 등록일(YYYY-MM-DD 형태를 우선 탐색)
    text = soup.get_text(" ", strip=True)
    m = DATE_RE.search(text)
    date_str = m.group(0) if m else ""

    # 담당부서
    dept = ""
    # 페이지에 "담당부서"가 텍스트로 존재하는 경우가 많음
    dept_m = re.search(r"담당부서\s*([^\s]+)", text)
    if dept_m:
        dept = dept_m.group(1).strip()

    # 첨부 viewer 경로로부터 down URL 후보 구성
    viewer_matches = VIEWER_RE.findall(html)
    download_urls = []
    for dir_id, file_hash, _viewer_hash in viewer_matches:
        down = f"{BASE}/attach/down/{dir_id}/{file_hash}"
        download_urls.append(down)

    # 후보 중복 제거
    download_urls = list(dict.fromkeys(download_urls))

    time.sleep(sleep_s)

    if not date_str:
        # 날짜 판별 실패 시 제외(원하면 로그로 남기도록 확장)
        return None

    return DocMeta(
        title=title,
        date=date_str,
        dept=dept,
        view_url=view_url,
        download_urls=download_urls
    )

def download_file(url: str, out_path: Path, referer: str, timeout: int = 60) -> bool:
    headers = {"Referer": referer, "Accept": "*/*"}
    try:
        with SESSION.get(url, headers=headers, timeout=timeout, stream=True) as r:
            r.raise_for_status()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 128):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception:
        return False

def extract_text_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts = []
    for p in reader.pages:
        t = p.extract_text() or ""
        parts.append(t)
    return "\n".join(parts)

def extract_text_hwpx(path: Path) -> str:
    # HWPX는 zip 기반. 내부 XML에서 텍스트 노드만 최대한 수집(노이즈는 후처리 권장).
    texts = []
    with zipfile.ZipFile(path, "r") as z:
        xml_files = [n for n in z.namelist() if n.lower().endswith(".xml") and ("Contents/" in n or "Preview/" in n)]
        for xf in xml_files:
            raw = z.read(xf)
            soup = BeautifulSoup(raw, "xml")
            # 모든 텍스트 노드 수집
            t = " ".join(soup.stripped_strings)
            if t:
                texts.append(t)
    return "\n".join(texts)

def normalize_text(s: str) -> str:
    # 공백/줄바꿈 정리 (모델링 전에 불필요 기호 제거는 별도 단계에서 권장)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def main():
    args = parse_args()
    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) view URL 수집(상대적으로 넓게 긁고, 날짜는 view에서 최종 필터)
    view_urls = crawl_list(start, end, args.sleep, args.max_pages)

    docs: List[DocMeta] = []
    for vu in tqdm(view_urls, desc="Parse view pages"):
        try:
            meta = extract_meta_from_view(vu, args.sleep)
            if not meta:
                continue
            if within_range(meta.date, start, end):
                docs.append(meta)
        except Exception:
            continue

    # 2) 날짜순 정렬
    docs.sort(key=lambda x: x.date)

    jsonl_path = out_dir / "corpus.jsonl"
    txt_path = out_dir / "corpus.txt"

    with open(jsonl_path, "w", encoding="utf-8") as fj, open(txt_path, "w", encoding="utf-8") as ft:
        for i, d in enumerate(tqdm(docs, desc="Download & extract")):
            doc_id = f"motie_{d.date}_{i:04d}"
            title_slug = safe_filename(d.title)

            text = ""
            used_url = ""
            saved_file = None

            # 다운로드 후보 중 먼저 성공하는 파일 사용
            for cand in d.download_urls:
                # 확장자 힌트가 없으니, 먼저 PDF로 가정하여 저장 후 판별
                tmp = out_dir / "files" / f"{doc_id}"
                # 일단 바이너리로 저장
                ok = download_file(cand, tmp, referer=d.view_url)
                if not ok:
                    continue

                # 파일 시그니처로 PDF 여부 판별
                head = tmp.read_bytes()[:5]
                if head.startswith(b"%PDF"):
                    saved_file = tmp.with_suffix(".pdf")
                    tmp.rename(saved_file)
                    text = extract_text_pdf(saved_file)
                    used_url = cand
                    break
                else:
                    # HWPX는 zip(‘PK’)로 시작하는 경우가 많음
                    if head.startswith(b"PK"):
                        saved_file = tmp.with_suffix(".hwpx")
                        tmp.rename(saved_file)
                        text = extract_text_hwpx(saved_file)
                        used_url = cand
                        break
                    else:
                        # 알 수 없는 포맷: 보관만 하고 추출 스킵
                        saved_file = tmp.with_suffix(".bin")
                        tmp.rename(saved_file)
                        used_url = cand
                        text = ""
                        break

            text = normalize_text(text)

            # 키워드 필터
            if args.keyword:
                if (args.keyword not in d.title) and (args.keyword not in text):
                    continue

            rec = {
                "doc_id": doc_id,
                "date": d.date,
                "title": d.title,
                "dept": d.dept,
                "view_url": d.view_url,
                "download_url_used": used_url,
                "file_saved": str(saved_file) if saved_file else "",
                "text": text,
                "lang": "ko",
            }
            fj.write(json.dumps(rec, ensure_ascii=False) + "\n")

            # 단일 코퍼스 TXT (토픽모델링/워드클라우드 입력용)
            if text:
                ft.write(f"{d.title}\n{text}\n\n{'='*60}\n\n")

    print(f"[OK] JSONL: {jsonl_path}")
    print(f"[OK] TXT  : {txt_path}")

if __name__ == "__main__":
    main()
