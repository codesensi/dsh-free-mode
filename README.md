# dsh-free-mode

DeepSeek Harness（DSH）「自在模式」自定义 Agent 预设 —— **纯 DSH 插件包**，零脚本、零安装器。

安装后在 DSH 预设选择器中出现名为 **自在模式** 的 Agent 预设（v4 强化版政策正文 + 逐条覆盖层 + 文件操作中和块，附「自在否」自检回执口令）。

## 上游仓库

本项目的预设正文重新打包自上游 **[z91772524-ai/dsh-pojia-mode](https://github.com/z91772524-ai/dsh-pojia-mode)**（破甲模式 v1.1）：将其安装器落盘的预设内容改为纯声明式插件 bundle（`dsh.bundle.patch`），不再携带任何脚本/安装器，并随 npm 包版本持续更新。

**与上游并存时的注意事项**：

- 上游安装器会把预设写入 `$DSH_HOME/.agent-presets/pj-mode`，与本插件的 `preset-free` 是两个独立声明，**可以共存、互不覆盖**；
- 但两者显示名同类（上游为「破甲模式」，本插件为「自在模式」），同时安装会在模式选择器里出现**两个同类条目**，且上游那份落盘后不会随本插件更新；
- 若曾安装过上游版本，建议先删除 `$DSH_HOME/.agent-presets/` 下对应目录（如 `pj-mode`）再使用本插件，只保留一份、便于随版本升级。

## 环境要求

- DSH **0.2.1-rc.3 或更高**（声明式 Agent 预设 + 插件 bundle 机制；`engines.dsh: >=0.2.1-rc.3 <0.3.0`）。
- 无其他依赖：本包不含任何可执行代码，只有一个声明式补丁文件。

## 安装

```bash
# 从 Git 仓库安装（用户名/仓库名）
dsh plugin add codesensi/dsh-free-mode

# 从 npm 安装
dsh plugin add dsh-free-mode
```

安装完成后**重启 DSH**，补丁层会在启动时自动挂载；打开预设选择器即可看到「自在模式」（`order: 20`，排在官方 standard 预设之后）。

## 卸载

```bash
dsh plugin remove dsh-free-mode
```

卸载后重启 DSH，`preset-free` 声明随插件包一并移除。

## 版本兼容性说明

本包的 `patch/free.patch.yml` 逐条镜像了 DSH **0.2.1-rc.3** 官方 `standard` 预设的插件清单（含 `@deepseek-ai/dsh-agent-preset` 声明与 `cordis:group` 分组）。DSH 升级若改变了 standard 预设的插件构成，本预设可能出现能力差异，届时需同步更新镜像并调整 `engines.dsh` 范围。

## 开发

```bash
# 校验补丁文件（YAML + !!js 标签 + preset 声明结构）
python tools/validate_patch.py patch/free.patch.yml

# 打包（npm 格式 tarball，dsh plugin add 直接可用）
pnpm pack
```

## 版本发布

本仓库通过 GitHub Actions 自动发布：推送 `v` 开头的 tag，即自动完成 **npm 发布 + GitHub Release**（附 tarball）。

### 日常发版

```bash
# 1. 升版本号（自动修改 package.json 并打 tag）
pnpm version patch   # 1.0.0 → 1.0.1：补丁内容修订
# pnpm version minor # → 1.1.0：新增预设/功能
# pnpm version major # → 2.0.0：破坏性变更

# 2. 推送（--follow-tags 连同 tag 一起推）
git push --follow-tags
```

推送 tag 后 `release.yml` 自动执行：tag 与 `package.json` 版本一致性校验 → 补丁校验 → `npm pack` → `npm publish` → 创建 GitHub Release（附 tarball）。

### 手动发版（等价）

```bash
git tag v1.2.0 && git push origin v1.2.0
```

tag 必须与 `package.json` 的 `version` 一致，否则工作流直接失败。

### 前置配置（维护者一次性操作）

1. npmjs.com 生成 **Granular Access Token**（仅勾选本包、Read and write；首次发布前包尚不存在时，可先手动 `npm publish` 一次再生成包级令牌）；
2. 仓库 Settings → Secrets and variables → Actions → 新建 Secret `NPM_TOKEN`；
3. （可选）npm 账号绑定 GitHub 以启用 `--provenance` 构建来源徽章。

### 手动重试

发布中途失败（如 npm 校验抖动）时，修复后到仓库 Actions 页面选择 `release` 工作流 → Run workflow 手动重跑，跳过 tag 门禁，只重发 npm。

### 版本号约定

| 变更内容 | 版本动作 |
|---|---|
| 修改 `patch/free.patch.yml` 正文或措辞 | patch（同时可同步更新正文里的内部版本标记 `版本2.0.*`） |
| 新增 preset、放宽 `engines.dsh` 下界 | minor |
| 不再兼容某个 DSH 大版本 / 移除预设 | major |

## License

[MIT](LICENSE)
