---
name: glm-vision
description: Describe images, extract text, and compare images through a Python CLI with vision-provider fallback. Use when external vision analysis is requested or the host lacks image understanding; not required when the host's native vision already meets the task.
---

# GLM Vision：图像理解与模型切换

用 Python 脚本调用智谱或硅基流动视觉模型，把图片转换成文字。适用于需要外部视觉服务的 agent，也可独立在终端使用。
宿主已有足够的视觉能力时可直接使用原生能力；不要求每张图片都上传外部服务。

## 要求与配置

- Python 3.8+，只用标准库，无需额外安装 Python 包。
- 需要网络，以及至少一个服务商账户和有效 API Key。
- 环境变量：`ZHIPU_API_KEY`、`SILICONFLOW_API_KEY`；不从个人文件或其他工具配置中提取密钥。
- 模型可用性、定价和配额以服务商当前政策为准；这里不保证免费或永久可用。
- 调用会把图片内容或图片 URL 和提示词发送给服务商。只有当前用户授权范围允许时才调用；已有授权不重复询问。

服务商入口：[智谱](https://open.bigmodel.cn/) / [硅基流动](https://cloud.siliconflow.cn/)。

## 使用

以下命令从本仓库根目录运行。安装到其他位置后定位本 SKILL.md 旁的 `scripts/vision.py`，使用实际路径。

```bash
python skills/glm-vision/scripts/vision.py --images screenshot.png --prompt "提取截图里的文字"
python skills/glm-vision/scripts/vision.py --images a.png b.png --prompt "比较两张图片"
python skills/glm-vision/scripts/vision.py --images screenshot.png --model zhipu/glm-4v-flash
```

支持本地图片、HTTP(S) 图片 URL、data URI；本地图片自动编码。不存在的本地文件会在联网前失败。
不支持视频或其他文档输入。URL 必须是服务商可访问的图片地址，不假定私有 URL 可用。
可设置 `--max-tokens`、`--temperature`、`--system`，参数详见 `--help`。

## 工作流与切换

1. 从用户输入确认实际图片与问题；不能凭文件名猜图片内容。
2. 判断是否需要外部服务、是否在授权范围内、脚本和密钥是否可用。
3. 执行脚本：stdout 是识别文字；stderr 是模型选择、失败分类和诊断。
4. 基于结果回答，标记 OCR 或视觉不确定项；全部失败如实报告，不伪造图片内容。

默认模型链见 `scripts/vision.py` 的 MODEL_CHAIN。429 跳下一模型；临时网络/服务故障重试一次；认证失败跳过整个服务商；其他请求错误跳下一模型。
最多每个模型两次调用，每次网络超时 120 秒，重试等待 3 秒，不无限重试。
旧模型可能下线，可用 `--model provider/model` 指定账户实际支持的模型。默认输出限制是兼容预设，实际能力以服务商为准。
切换可能调用多个模型或服务商；若用户限定单一服务商/模型，使用 `--model`。
退出码：0 成功，1 无可用结果，2 参数或本地输入错误。诊断不输出密钥或服务商原始错误正文。
