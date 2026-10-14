# Portable Agent Skills

可移植 AI Agent 技能集：项目断点续做、多会话交接和图像理解。

核心是普通 Markdown 指令、模板和独立 Python 脚本，不依赖特定 agent 的私有 API。
可以安装到支持 skills 的工具，也可以让其他 agent 读取 SKILL.md，或直接运行视觉脚本。

## 技能

| Skill | 解决的问题 | 所需能力 |
| --- | --- | --- |
| [project-checkpoint](skills/project-checkpoint/SKILL.md) | 新会话恢复任务，按角色维护检查点与验证证据 | 读写项目文件；Git 检查仅适用于 Git 项目 |
| [team-handoff](skills/team-handoff/SKILL.md) | 保存团队状态、角色交接和协调者接管 | 读写项目文件；会话通信可由人工转发 |
| [glm-vision](skills/glm-vision/SKILL.md) | 图片描述、OCR、多图比较与模型故障切换 | Python 3.8+、网络、服务商 API Key |

## 下载和安装

无需 Git：在 GitHub 点击 **Code → Download ZIP**，解压后使用。
也可在 [Releases](https://github.com/SadCat18/portable-agent-skills/releases) 下载版本包。

使用 Git：
```bash
git clone https://github.com/SadCat18/portable-agent-skills.git
```

支持 skills 的工具：将需要的技能文件夹（例如整个 `skills/project-checkpoint`）复制到该工具文档规定的 skill 目录，再按工具要求重新加载。
**必须保留 references、assets、scripts 等配套资源**，不要只复制 SKILL.md。
安装目录和调用语法由宿主决定，本项目不修改全局工具配置。

不支持自动加载 skills 的工具：在提示词中指定实际文件路径，例如：
```text
读取 portable-agent-skills/skills/project-checkpoint/SKILL.md，并按它的流程工作。
你是前端，TASK_ID=member-center，负责会员中心页面；继续同项目已有的检查点。
```
无法读取本地文件的聊天工具，可手动提供本次需要的 SKILL.md 和引用资料；但无法自动检查或维护项目文件。

## 快速使用

### 项目续做

```text
读取 skills/project-checkpoint/SKILL.md。
你是后端，TASK_ID=order-api，负责订单接口。
每个阶段保留实际验证证据，并在检查点留下唯一下一步。
```
默认检查点在项目的 `.agent/progress/`；已有目录优先沿用。新聊天读取同一项目和检查点恢复。

### 多会话交接

```text
读取 skills/team-handoff/SKILL.md，执行全组交接。
角色是 coordinator、frontend、backend、tester，沿用现有职责。
使用项目的 .agent-handoff；没有会话通信工具时给出人工转发提示词和回执。
```
角色数量可配置。封存、接管和恢复调度分别记录；文件存在不代表其他会话已读或收到任务。

### 图像理解

环境变量在本地终端设置，不提交密钥。

PowerShell：
```powershell
$env:ZHIPU_API_KEY = '<your-api-key>'
python skills/glm-vision/scripts/vision.py --images screenshot.png --prompt "提取截图中的文字"
```

macOS / Linux：
```bash
export ZHIPU_API_KEY='<your-api-key>'
python3 skills/glm-vision/scripts/vision.py --images screenshot.png --prompt '提取截图中的文字'
```

也可配置 `SILICONFLOW_API_KEY` 增加可用服务商。脚本只依赖标准库，stdout 输出答案，stderr 输出诊断。
支持 `--model provider/model` 限定单一模型。模型可能下线或收费，价格、额度与可用性以服务商当前政策为准。
外部调用会向服务商发送图片或图片 URL 和提示词；原生视觉已足够时无需执行脚本。

## 兼容性与验证范围

“通用”指文件格式、相对资源路径和能力驱动流程可移植，不保证每个 agent 都能自动安装、调用或执行全部功能。
`$skill-name` 是部分宿主支持的简写；手动读取文件是通用入口。
不依赖 Codex、Claude Code、Cursor 或其他特定工具；各宿主的自动发现行为需按其文档设置并实测。
目前验证：Windows / Python 3.11 的离线脚本检查、资源链接、无密钥输入、模拟故障切换。
未验证：各 agent 的自动安装/触发、macOS/Linux 实机行为、Python 3.8 实机运行，以及真实视觉服务端到端调用。

维护者可运行：
```bash
python -B -m unittest discover -s tests -v
```
这些测试不联网、不使用真实密钥，也不证明服务商当前模型可用。

## 贡献与许可

欢迎通过 Issue 提供问题、宿主工具与最小复现，或通过 Pull Request 提交改进。
不要提交密钥、真实项目交接、私人聊天或敏感截图。保持每个 skill 可独立复制，新增依赖时明确说明。

[MIT License](LICENSE)。许可适用于本仓库内容，不代替第三方 API 的使用条款或费用。
