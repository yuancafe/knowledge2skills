#!/usr/bin/env python3
"""
Multi-format Content Extractor for knowledge2skills

Supports: .pdf, .md, .txt, .docx, .epub, .mobi, .azw3, .json
Can process a single file or a list of files.
"""

import os
import json
import re
import argparse
import sys
import subprocess
from pathlib import Path

# Optional dependency imports
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

try:
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    epub = None

try:
    import mobi
except ImportError:
    mobi = None

# MinerU (Magic-PDF) support
MAGIC_PDF_AVAILABLE = False
LOCAL_MINERU_PYTHON = os.path.expanduser("~/.pyenv/versions/3.11.9/bin/python")

try:
    from magic_pdf.pipe.UNIPipe import UNIPipe
    from magic_pdf.rw.AbsReaderWriter import FileReaderWriter
    MAGIC_PDF_AVAILABLE = True
except ImportError:
    # Check for the local deployment specified by the user
    if os.path.exists(LOCAL_MINERU_PYTHON):
        MAGIC_PDF_AVAILABLE = True

def install_package(package_name: str):
    """Interactively install a missing package."""
    ans = input(f"\n[!] Missing dependency: {package_name}. Install now? (y/n): ").lower()
    if ans == 'y':
        print(f"Installing {package_name}...")
        subprocess.run([sys.executable, "-m", "pip", "install", package_name])
        return True
    return False

import psutil
import shutil

CONFIG_PATH = Path.home() / ".knowledge2skills_config.json"

def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except:
            return {}
    return {}

def save_config(config):
    CONFIG_PATH.write_text(json.dumps(config, indent=2))

def check_hardware():
    """Check if RAM and Disk are sufficient for MinerU."""
    # RAM check: recommend 16GB+, minimum 8GB
    total_ram = psutil.virtual_memory().total / (1024**3)
    # Disk check: need ~10GB for models
    free_disk = shutil.disk_usage(Path.home()).free / (1024**3)
    
    return {
        "sufficient": total_ram >= 8 and free_disk >= 10,
        "ram": total_ram,
        "disk": free_disk
    }

def is_pdf_complex(path: Path) -> bool:
    """Heuristic to detect complex PDF (tables, formulas, images)."""
    if not pdfplumber:
        return False
    try:
        with pdfplumber.open(path) as pdf:
            # Check first 5 pages for complexity signals
            for i, page in enumerate(pdf.pages[:5]):
                # 1. Check for tables
                if page.extract_tables(): return True
                # 2. Check for images/rects (sign of complex layout)
                if len(page.images) > 2 or len(page.rects) > 10: return True
                # 3. Check for math symbols (crude check)
                text = page.extract_text() or ""
                if re.search(r'[∫∑√πθλαβγδεζ]', text): return True
    except:
        pass
    return False

def extract_with_mineru(path: Path, output_dir: Path) -> dict:
    """Intelligent high-precision extraction using MinerU."""
    config = load_config()
    
    # 1. If not forced by user via --high-precision, check if it's actually complex
    # (Note: we'll handle the 'high_precision' flag being passed in main)
    
    # 2. Check if already configured/used successfully
    mineru_ready = os.path.exists(LOCAL_MINERU_PYTHON) or MAGIC_PDF_AVAILABLE
    
    if not mineru_ready:
        # Check hardware
        hw = check_hardware()
        if not hw["sufficient"]:
            print(f"  [MinerU] Hardware insufficient (RAM: {hw['ram']:.1f}GB, Disk: {hw['disk']:.1f}GB). Skipping.")
            return extract_from_pdf(path)
        
        # Hardware sufficient but not installed, ask user
        print(f"\n[?] Complex PDF detected. Your hardware is sufficient for MinerU (High-Precision Parsing).")
        ans = input("Would you like to download and deploy MinerU? (This takes ~5-10GB disk space) (y/n): ").lower()
        if ans == 'y':
            print("To deploy MinerU, please follow the official guide or run the following manually:")
            print("1. git clone https://github.com/opendatalab/MinerU")
            print("2. pip install magic-pdf[full] --extra-index-url https://wheels.myhloli.com")
            print("For now, falling back to standard parser.")
            return extract_from_pdf(path)
        else:
            config["mineru_disabled"] = True
            save_config(config)
            return extract_from_pdf(path)

    # 3. Actually run MinerU
    print(f"  [High-Precision] Using MinerU to parse {path.name}...")
    
    result = None
    # Try local CLI invocation
    if os.path.exists(LOCAL_MINERU_PYTHON):
        try:
            cmd = [
                LOCAL_MINERU_PYTHON, "-m", "mineru.cli.client",
                "-p", str(path),
                "-o", str(output_dir),
                "-b", "pipeline",
                "--device", "cpu"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            parsed_dir = output_dir / path.stem
            md_files = list(parsed_dir.glob("*.md"))
            if md_files:
                full_md = md_files[0].read_text(encoding="utf-8")
                result = {
                    "sections": [{"heading": "MinerU Parsed Content", "content": full_md, "level": 1}],
                    "full_text": full_md,
                    "tables": [], 
                    "method": "mineru_local_cli"
                }
                # Record success
                config["mineru_last_success"] = True
                save_config(config)
        except Exception as e:
            print(f"  Local MinerU CLI failed: {e}")

    # Fallback to library import... (rest of logic same as before)
    if not result:
        try:
            from magic_pdf.pipe.UNIPipe import UNIPipe
            from magic_pdf.rw.AbsReaderWriter import FileReaderWriter
            pdf_data = path.read_bytes()
            reader = FileReaderWriter(str(output_dir))
            pipe = UNIPipe(pdf_data, {"_pdf_type": "read"}, reader)
            pipe.pipe_parse()
            content_list = pipe.pipe_mk_markdown(str(output_dir), path.name)
            full_md = ""
            for item in content_list:
                if isinstance(item, dict) and item.get('type') == 'text':
                    full_md += item['content'] + "\n\n"
                elif isinstance(item, str):
                    full_md += item + "\n\n"
            result = {
                "sections": [{"heading": "MinerU Parsed Content", "content": full_md, "level": 1}],
                "full_text": full_md,
                "tables": [], 
                "method": "mineru_library"
            }
            config["mineru_last_success"] = True
            save_config(config)
        except:
            print("  MinerU library parsing failed. Falling back.")
            return extract_from_pdf(path)
            
    return result

def extract_from_pdf(path: Path) -> dict:
    """Extract content from PDF using standard libraries."""
    sections = []
    full_text = ""
    tables = []
    
    if pdfplumber:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                full_text += text + "\n\n"
                sections.append({"heading": f"Page {i+1}", "content": text, "level": 2})
                try:
                    p_tables = page.extract_tables()
                    for t in p_tables:
                        if t: tables.append({"page": i+1, "data": t})
                except: pass
    elif PdfReader:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            full_text += text + "\n\n"
            sections.append({"heading": f"Page {i+1}", "content": text, "level": 2})
    
    return {"sections": sections, "full_text": full_text, "tables": tables}

def extract_from_epub(path: Path) -> dict:
    """Extract content from EPUB."""
    global epub
    import ebooklib
    from ebooklib import epub as epub_lib
    from bs4 import BeautifulSoup

    book = epub_lib.read_epub(str(path))
    full_text = ""
    sections = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text()
            full_text += text + "\n\n"
            heading = soup.find(['h1', 'h2'])
            title = heading.get_text().strip() if heading else f"Chapter {len(sections)+1}"
            sections.append({"heading": title, "content": text, "level": 2})

    return {"sections": sections, "full_text": full_text, "tables": []}


def extract_from_mobi(path: Path) -> dict:
    """Extract content from MOBI/AZW3."""
    global mobi
    if not mobi:
        if install_package("mobi"):
            import mobi
        else:
            return {"sections": [], "full_text": "Error: mobi library not installed", "tables": []}

    try:
        tmp_dir, html_content = mobi.extract(str(path))
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        return {"sections": [{"heading": "Book Content", "content": text, "level": 2}], "full_text": text, "tables": []}
    except Exception as e:
        return {"sections": [], "full_text": f"Error parsing: {e}", "tables": []}

def extract_from_docx(path: Path) -> dict:
    """Extract content from DOCX."""
    if not docx: return {"sections": [], "full_text": "Error: python-docx not installed", "tables": []}
    doc = docx.Document(path)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    sections = []
    curr_sec = {"heading": "Document", "content": [], "level": 1}
    for para in doc.paragraphs:
        if para.style.name.startswith('Heading'):
            if curr_sec["content"]:
                curr_sec["content"] = "\n".join(curr_sec["content"])
                sections.append(curr_sec)
            curr_sec = {"heading": para.text, "content": [], "level": 2}
        else:
            curr_sec["content"].append(para.text)
    
    if curr_sec["content"]:
        curr_sec["content"] = "\n".join(curr_sec["content"])
        sections.append(curr_sec)
        
    return {"sections": sections, "full_text": full_text, "tables": []}

def extract_from_text(path: Path) -> dict:
    """Extract from TXT or MD."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")
    sections = []
    curr_sec = {"heading": "Start", "content": [], "level": 2}
    
    for line in lines:
        if line.startswith("#"):
            if curr_sec["content"]:
                curr_sec["content"] = "\n".join(curr_sec["content"])
                sections.append(curr_sec)
            curr_sec = {"heading": line.lstrip("# ").strip(), "content": [], "level": line.count("#")}
        else:
            curr_sec["content"].append(line)
            
    if curr_sec["content"]:
        curr_sec["content"] = "\n".join(curr_sec["content"])
        sections.append(curr_sec)
        
    return {"sections": sections, "full_text": text, "tables": []}

def process_files(paths: list, high_precision: bool = False, work_dir: Path = None) -> dict:
    """Process multiple files into a single unified extraction."""
    combined = {
        "metadata": {"sources": [], "total_files": len(paths)},
        "sections": [],
        "tables": [],
        "full_text": ""
    }
    
    for p_str in paths:
        path = Path(p_str).resolve()
        if not path.exists(): continue
        
        ext = path.suffix.lower()
        combined["metadata"]["sources"].append({"name": path.name, "type": ext})
        
        print(f"Processing: {path.name}...")
        
        if ext == ".pdf":
            # Auto-detect complexity
            complex_pdf = is_pdf_complex(path)
            config = load_config()
            
            # Use MinerU if: 
            # 1. User forced it via --high-precision
            # 2. OR it's complex AND (it worked before OR user didn't disable it)
            should_use_mineru = high_precision or (
                complex_pdf and 
                not config.get("mineru_disabled")
            )
            
            if should_use_mineru and work_dir:
                res = extract_with_mineru(path, work_dir)
            else:
                if complex_pdf:
                    print(f"  [Notice] {path.name} appears complex, but MinerU is skipped.")
                res = extract_from_pdf(path)
        elif ext == ".docx": res = extract_from_docx(path)
        elif ext == ".epub": res = extract_from_epub(path)
        elif ext in [".mobi", ".azw3"]: res = extract_from_mobi(path)
        elif ext in [".txt", ".md", ".markdown"]: res = extract_from_text(path)
        elif ext == ".json":
            try:
                raw_data = json.loads(path.read_text())
                res = {"sections": [], "full_text": json.dumps(raw_data), "tables": []}
            except: res = {"sections": [], "full_text": "", "tables": []}
        else: continue
        
        for s in res.get("sections", []):
            s["heading"] = f"[{path.name}] {s['heading']}"
            combined["sections"].append(s)
        
        combined["full_text"] += f"\n\n--- Source: {path.name} ---\n\n" + res.get("full_text", "")
        combined["tables"].extend(res.get("tables", []))
        
    return combined

def main():
    parser = argparse.ArgumentParser(description="Extract content from various formats")
    parser.add_argument("files", nargs="+", help="Paths to files to process")
    parser.add_argument("--output", "-o", help="Output JSON path")
    parser.add_argument("--high-precision", action="store_true", help="Use MinerU for PDFs")
    args = parser.parse_args()
    
    # Need a work dir for MinerU
    work_dir = Path("./extraction_work").resolve()
    work_dir.mkdir(exist_ok=True)
    
    result = process_files(args.files, high_precision=args.high_precision, work_dir=work_dir)
    
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
