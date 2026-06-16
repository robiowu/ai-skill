#!/usr/bin/env python3
"""
Excel 行范围截图 CLI 工具

供 excel-to-markdown skill 调用，对 Excel sheet 的指定行范围进行截图。
内部调用 excel_export.py 的 export_sheet_range_screenshot API。

用法:
  单次模式:
    python excel_range_screenshot.py <excel_path> <sheet_name> <start_row> <end_row> <output_dir> [--filename <name.png>]

  批量模式:
    python excel_range_screenshot.py <excel_path> <sheet_name> --batch <json_file> --output-dir <output_dir>

    json_file 格式:
    [
        {"start_row": 1, "end_row": 45, "filename": "module_1.png", "max_col": 20},
        {"start_row": 46, "end_row": 120, "filename": "module_2.png"}
    ]
    max_col 可选，由 Agent 分析截图后指定的最大内容列号（脚本自动加1列安全距离）。
    未指定时根据该行范围内的实际单元格内容自动计算。

输出:
  JSON 格式的状态报告（stdout），方便 Agent 解析。
"""

import sys
import os
import json
import argparse

# Windows: stdout/stderr 统一使用 UTF-8，避免中文乱码
# 在 cmd 中运行前建议执行 `chcp 65001`，或使用 Windows Terminal
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 从同目录导入 excel_export
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from excel_export import export_sheet_range_screenshot, get_sheet_info, _auto_crop_whitespace


def main():
    parser = argparse.ArgumentParser(
        description='Excel 行范围截图工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('excel_path', help='Excel 文件路径')
    parser.add_argument('sheet_name', help='目标 sheet 名称')

    # 单次模式参数
    parser.add_argument('start_row', nargs='?', type=int, help='起始行号')
    parser.add_argument('end_row', nargs='?', type=int, help='结束行号')
    parser.add_argument('output_dir', nargs='?', help='输出目录')
    parser.add_argument('--filename', default=None, help='输出文件名（默认 screenshot.png）')

    # 批量模式参数
    parser.add_argument('--batch', metavar='JSON_FILE', help='批量模式：JSON 文件路径，包含行范围列表')
    parser.add_argument('--output-dir', dest='batch_output_dir', help='批量模式的输出目录')

    # 辅助命令
    parser.add_argument('--list-sheets', action='store_true', help='列出所有 sheet 信息（JSON 输出）')

    args = parser.parse_args()

    # ── list-sheets 模式 ──
    if args.list_sheets:
        try:
            info = get_sheet_info(args.excel_path)
            # content_bounds 是 tuple，需要转为 list 才能 JSON 序列化
            for item in info:
                if item['content_bounds']:
                    item['content_bounds'] = list(item['content_bounds'])
            output = {'success': True, 'sheets': info}
            print(json.dumps(output, ensure_ascii=False, indent=2))
        except Exception as e:
            output = {'success': False, 'error': str(e)}
            print(json.dumps(output, ensure_ascii=False, indent=2))
            sys.exit(1)
        return

    # ── 批量模式 ──
    if args.batch:
        batch_output_dir = args.batch_output_dir or args.output_dir
        if not batch_output_dir:
            print(json.dumps({
                'success': False,
                'error': '批量模式需要指定 --output-dir'
            }, ensure_ascii=False, indent=2))
            sys.exit(1)

        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                ranges_data = json.load(f)

            ranges = []
            skipped = []
            for i, item in enumerate(ranges_data):
                if not item.get('needs_screenshot', True):
                    skipped.append(item.get('name', f"module_{i+1}"))
                    continue
                r = (item['start_row'], item['end_row'],
                     item.get('filename', f"module_{i+1}.png"))
                if 'max_col' in item and item['max_col'] is not None:
                    r = r + (item['max_col'],)
                ranges.append(r)

            results = export_sheet_range_screenshot(
                args.excel_path, args.sheet_name, ranges, batch_output_dir
            )

            # 自动裁剪每张截图的空白区域
            for r in results:
                if r['success']:
                    for fname in r['files']:
                        fpath = os.path.join(batch_output_dir, fname)
                        if os.path.exists(fpath):
                            _auto_crop_whitespace(fpath)

            output = {
                'success': all(r['success'] for r in results),
                'output_dir': str(os.path.abspath(batch_output_dir)),
                'results': results,
                'total': len(results),
                'succeeded': sum(1 for r in results if r['success']),
                'failed': sum(1 for r in results if not r['success']),
                'skipped': skipped,
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))

            if not output['success']:
                sys.exit(1)

        except Exception as e:
            print(json.dumps({
                'success': False,
                'error': str(e)
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
        return

    # ── 单次模式 ──
    if args.start_row is None or args.end_row is None or args.output_dir is None:
        parser.error('单次模式需要提供 start_row, end_row, output_dir')

    filename = args.filename or 'screenshot.png'

    try:
        results = export_sheet_range_screenshot(
            args.excel_path, args.sheet_name,
            [(args.start_row, args.end_row, filename)],
            args.output_dir
        )

        # 自动裁剪空白区域
        for r in results:
            if r['success']:
                for fname in r['files']:
                    fpath = os.path.join(args.output_dir, fname)
                    if os.path.exists(fpath):
                        _auto_crop_whitespace(fpath)

        result = results[0]
        output = {
            'success': result['success'],
            'output_dir': str(os.path.abspath(args.output_dir)),
            'filename': result['filename'],
            'files': result['files'],
            'start_row': result['start_row'],
            'end_row': result['end_row'],
        }
        if result['error']:
            output['error'] = result['error']

        print(json.dumps(output, ensure_ascii=False, indent=2))

        if not result['success']:
            sys.exit(1)

    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
