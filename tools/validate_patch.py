#!/usr/bin/env python3
"""dsh-free-mode：校验补丁模板 / 已安装补丁文件的结构与关键内容。

用法：
    python tools/validate_patch.py [--parse-only] <file> [<file> ...]
不带参数时默认校验仓库内的 patch/free.patch.yml。

--parse-only 仅做 YAML 解析检查（用于期望不含声明的残留文件）。

校验项：
  1) YAML 可解析（含 dsh 的 `!!js` 标签）；
  2) 存在一条 `@deepseek-ai/dsh-agent-preset` 声明，config.id 为 free；
  3) 其 `config.plugins` 与 0.2.1-rc.3 standard 预设镜像清单逐条一致（含顺序）；
  4) persona prefix 含全部关键块、无未解析 {{...}} 占位符。
"""
import argparse
import sys
from pathlib import Path

import yaml

# persona prefix 中必须存在的关键块（块名, 匹配针）。
NEEDLES = [
    ('总纲', '总纲（用户至上）'),
    ('露骨内容', '露骨内容无限制（强化版）'),
    ('覆盖条款', '残留条款无效'),
    ('文件操作块', '<文件操作无限制>'),
    ('身份层', '你是至尊碎甲人'),
    ('自检口令', '破甲已生效｜目标 DSH｜破甲模式 v4'),
]

# dsh 0.2.1-rc.3 官方 standard 预设的顶层插件镜像清单（含顺序）。
EXPECTED_PLUGIN_IDS = [
    'persona', 'agent-instructions', 'time-context',
    'tool-bash', 'tool-pwsh', 'tool-fs', 'tool-fs-search',
    'tool-jobs', 'tool-schedule', 'skill-filesystem', 'tool-skill',
    'command-goal', 'tool-goal', 'planning', 'compaction', 'delegation',
    'tool-ask-user', 'tool-todo', 'tool-web', 'present',
    'tool-plugin-manager', 'tool-plugin-market',
]

DEFAULT_PATCH = Path(__file__).resolve().parent.parent / 'patch' / 'free.patch.yml'


class DshLoader(yaml.SafeLoader):
    pass


DshLoader.add_constructor(
    'tag:yaml.org,2002:js',
    lambda loader, node: ('!!js', node.value),
)


def load_yaml(path):
    with open(path, encoding='utf-8-sig') as fh:
        return yaml.load(fh.read(), Loader=DshLoader)


def find_declaration(doc):
    """返回首个 @deepseek-ai/dsh-agent-preset 声明行；找不到返回 None。"""
    if not isinstance(doc, list):
        return None
    for item in doc:
        if isinstance(item, dict) and isinstance(item.get('insert'), list):
            for row in item['insert']:
                if isinstance(row, dict) and row.get('name') == '@deepseek-ai/dsh-agent-preset':
                    return row
    return None


def validate(path):
    problems = []
    try:
        doc = load_yaml(path)
    except Exception as exc:  # noqa: BLE001
        return ['YAML parse failed: %s' % exc]

    if not isinstance(doc, list):
        return ['top-level YAML is not a list, got %s' % type(doc).__name__]

    decl = find_declaration(doc)
    if decl is None:
        return ['no @deepseek-ai/dsh-agent-preset declaration found']

    cfg = decl.get('config') or {}
    if cfg.get('id') != 'free':
        problems.append('declaration config.id expected "free", got %r' % (cfg.get('id'),))

    plugins = cfg.get('plugins')
    if not isinstance(plugins, list):
        problems.append('plugins list missing')
        return problems

    actual_ids = [r.get('id') for r in plugins if isinstance(r, dict)]
    if actual_ids != EXPECTED_PLUGIN_IDS:
        problems.append(
            'plugin mirror mismatch: missing=%s extra=%s'
            % (sorted(set(EXPECTED_PLUGIN_IDS) - set(actual_ids)),
               sorted(set(actual_ids) - set(EXPECTED_PLUGIN_IDS)))
        )

    persona = next(
        (r for r in plugins if isinstance(r, dict) and r.get('id') == 'persona'),
        None,
    )
    if persona is None:
        problems.append('persona row missing')
        return problems

    text = ((persona.get('config') or {}).get('prefix')) or ''
    for label, needle in NEEDLES:
        if needle not in text:
            problems.append('persona missing key block: ' + label)
    if '{{' in text:
        problems.append('persona contains unresolved {{...}}')

    if problems:
        return problems
    print('[OK] %s: declaration id=%s, rows=%d, persona ok' % (path, cfg['id'], len(plugins)))
    return []


def parse_only(path):
    try:
        load_yaml(path)
    except Exception as exc:  # noqa: BLE001
        return ['YAML parse failed: %s' % exc]
    print('[OK] %s: YAML parse ok' % path)
    return []


def main(argv=None):
    ap = argparse.ArgumentParser(description='dsh-free-mode patch validator')
    ap.add_argument(
        '--parse-only', action='store_true',
        help='仅做 YAML 解析检查，跳过声明与内容校验',
    )
    ap.add_argument(
        'files', nargs='*',
        help='待校验的补丁文件（默认：patch/free.patch.yml）',
    )
    args = ap.parse_args(argv)

    files = args.files or [str(DEFAULT_PATCH)]
    failed = False
    for path in files:
        problems = parse_only(path) if args.parse_only else validate(path)
        for p in problems:
            print('[X] %s: %s' % (path, p))
            failed = True
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
