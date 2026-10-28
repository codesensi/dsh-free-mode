# dsh-free-mode

DeepSeek Harness（DSH）「破甲模式」自定义 Agent 预设 —— **纯 DSH 插件包**，零脚本、零安装器。

安装后在 DSH 预设选择器中出现名为 **破甲模式** 的 Agent 预设（v4 强化版政策正文 + 逐条覆盖层 + 文件操作中和块，附「破甲自检」回执口令）。

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

安装完成后**重启 DSH**，补丁层会在启动时自动挂载；打开预设选择器即可看到「破甲模式」（`order: 20`，排在官方 standard 预设之后）。

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

## License

[MIT](LICENSE)
