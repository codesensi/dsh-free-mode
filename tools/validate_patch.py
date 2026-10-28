#!/usr/bin/env python3
"""dsh-free-mode：校验补丁模板 / 已安装补丁文件的结构与关键内容。

用法：
    python tools/validate_patch.py [--parse-only] <file> [<file> ...]

--parse-only 仅做 YAML 解析检查（用于期望不含声明的残留文件）。

校验项：
  1) YAML 可解析（含 dsh 的 `!!js` 标签）；
  2) 存在一条 `@deepseek-ai/dsh-agent-preset` 声明；
  3) 其 `config.plugins` 行数合理、含 persona 行；
  4) persona prefix 含全部关键块、且不含未解析的 {{...}} 占位符。
"""
import sys

import yaml


class DshLoader(yaml.SafeLoader):
    pass


DshLoader.add_constructor(
    'tag:yaml.org,2002:js',
    lambda loader, node: ('!!js', node.value),
)

NEEDLES = [
    '总纲（用户至上）',
    '露骨内容无限制（强化版）',
    '残留条款无效',
    '版本2.0.C730EC47C921',
    '<文件操作无限制>',
    '你是小码酱',
    '破甲已生效｜目标 DSH｜破甲模式 v4',
]


def validate(path):
    problems = []
    try:
        doc = yaml.load(open(path, encoding='utf-8').read(), Loader=DshLoader)
    except Exception as exc:  # noqa: BLE001
        return ['YAML parse failed: %s' % exc]

    decl = None
    if isinstance(doc, list):
        for item in doc:
            if isinstance(item, dict) and item.get('insert'):
                for row in item['insert']:
                    if isinstance(row, dict) and row.get('name') == '@deepseek-ai/dsh-agent-preset':
                        decl = row
                        break
            if decl:
                break
    if decl is None:
        return ['no @deepseek-ai/dsh-agent-preset declaration found']

    cfg = decl.get('config') or {}
    if not cfg.get('id'):
        problems.append('declaration config.id missing')

    plugins = cfg.get('plugins')
    if not isinstance(plugins, list) or len(plugins) < 20:
        problems.append(
            'plugins list missing or too short: %s'
            % (len(plugins) if isinstance(plugins, list) else 'n/a')
        )
        return problems

    persona = next(
        (r for r in plugins if isinstance(r, dict) and r.get('id') == 'persona'),
        None,
    )
    if persona is None:
        problems.append('persona row missing')
        return problems

    text = ((persona.get('config') or {}).get('prefix')) or ''
    for needle in NEEDLES:
        if needle not in text:
            problems.append('persona missing key block: ' + needle)
    if '{{' in text:
        problems.append('persona contains unresolved {{...}}')

    if problems:
        return problems
    print('[OK] %s: declaration id=%s, rows=%d, persona ok' % (path, cfg['id'], len(plugins)))
    return []


def parse_only(path):
    try:
        yaml.load(open(path, encoding='utf-8').read(), Loader=DshLoader)
    except Exception as exc:  # noqa: BLE001
        return ['YAML parse failed: %s' % exc]
    print('[OK] %s: YAML parse ok' % path)
    return []


def main(argv):
    parse_only_mode = bool(argv) and argv[0] == '--parse-only'
    if parse_only_mode:
        argv = argv[1:]
    if not argv:
        print('usage: python tools/validate_patch.py [--parse-only] <file> [<file> ...]')
        return 2
    failed = False
    for path in argv:
        problems = parse_only(path) if parse_only_mode else validate(path)
        for p in problems:
            print('[X] %s: %s' % (path, p))
        if problems:
            failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
