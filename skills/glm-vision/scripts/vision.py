#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Portable vision CLI with bounded provider fallback. Credentials: environment only."""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_PROMPT = "请详细描述这张图片的内容，包括所有可见的文字（逐字准确输出）、物体、场景和布局。"

# 支持的提供商: 名称 -> 接口地址 / Key 来源 / 图片编码方式
PROVIDERS = {
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "env": "ZHIPU_API_KEY",
        "config": "ZHIPU",
        "image_prefix": False,  # 官方示例: base64 直接放入 url 字段
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1/chat/completions",
        "env": "SILICONFLOW_API_KEY",
        "config": "SILICONFLOW",
        "image_prefix": True,   # 文档示例: data:image/...;base64, 前缀
    },
}

# 模型链: 按优先级排列，前一个过载/失败就自动换下一个。
# max_out     = 该模型最大输出 token 数（脚本会按需截断 max_tokens）
# max_images  = 单次最多支持的图片数（多图时自动跳过该模型）
# 想加新模型：按同样格式追加一行即可
MODEL_CHAIN = [
    {"provider": "zhipu", "model": "glm-4.6v-flash", "max_out": 32768},
    {"provider": "zhipu", "model": "glm-4.1v-thinking-flash", "max_out": 16384},
    {"provider": "zhipu", "model": "glm-4v-flash", "max_out": 1024, "max_images": 1},
    {"provider": "siliconflow", "model": "Qwen/Qwen2.5-VL-7B-Instruct", "max_out": 8192},
    {"provider": "siliconflow", "model": "Qwen/Qwen2.5-VL-3B-Instruct", "max_out": 8192},
    {"provider": "siliconflow", "model": "THUDM/GLM-4V-9B", "max_out": 4096},
]

MAX_ATTEMPTS_PER_MODEL = 2  # 单个模型最多尝试次数（含重试）


def get_api_key(provider):
    return os.environ.get(PROVIDERS[provider]["env"], "").strip()


def build_image_part(source, provider):
    """把图片源转成 API 的 content part。支持 data URI / http(s) URL / 本地文件。
    本地文件按提供商要求编码: 智谱放裸 base64，硅基流动加 data:image/...;base64, 前缀。"""
    if source.startswith("data:"):
        return {"type": "image_url", "image_url": {"url": source}}
    if source.startswith("http://") or source.startswith("https://"):
        return {"type": "image_url", "image_url": {"url": source}}
    # 本地文件 → base64
    if not os.path.exists(source):
        sys.stderr.write("错误: 文件不存在: %s\n" % source)
        return None
    if os.path.isdir(source):
        sys.stderr.write("错误: 这是目录而不是图片文件: %s\n" % source)
        return None
    with open(source, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    if PROVIDERS[provider]["image_prefix"]:
        mime = mimetypes.guess_type(source)[0] or "image/jpeg"
        url = "data:%s;base64,%s" % (mime, b64)
    else:
        url = b64  # 智谱官方示例: base64 直接放入 url
    return {"type": "image_url", "image_url": {"url": url}}


def classify_error(http_status, err):
    """把 HTTP 状态码 + 错误体归类为: auth / overload / transient / bad_request。
    auth        → Key 无效，整提供商跳过
    overload    → 模型过载/限流，直接换下一个模型
    transient   → 临时故障，重试后再换下一个模型
    bad_request → 该模型不可用/请求内容问题，换下一个模型
    """
    if isinstance(err, dict):
        code = str(err.get("code", ""))
    else:
        code = ""
    if http_status in (401, 403) or code in ("1001", "1002", "1000"):  # 1000=余额不足
        return "auth"
    if http_status == 429 or code in ("1305", "1113"):  # 1305=模型访问量过大 1113=请求过于频繁
        return "overload"
    if http_status >= 500:
        return "transient"
    return "bad_request"


def call_api(provider, api_key, payload):
    """调用一次 Chat Completions 接口。
    返回 (data, None) 或 (None, error_dict: {kind, message})。"""
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(PROVIDERS[provider]["base_url"], data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not isinstance(data, dict):
                return None, {"kind": "transient", "message": "服务商响应不是 JSON 对象"}
            if "error" in data:  # 部分错误以 HTTP 200 + body error 返回
                err = data["error"]
                return None, {"kind": classify_error(200, err), "message": "服务商返回错误，分类: " + classify_error(200, err)}
            return data, None
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        try:
            err = json.loads(detail).get("error")
        except Exception:
            err = detail
        kind = classify_error(e.code, err)
        return None, {"kind": kind, "message": "HTTP %s (%s)" % (e.code, kind)}
    except urllib.error.URLError as e:
        return None, {"kind": "network", "message": "网络连接失败"}

    except (TimeoutError, OSError, ValueError):
        return None, {"kind": "transient", "message": "超时、读取失败或无效 JSON 响应"}


def extract_text(data):
    """从响应中取出文字（只使用最终 content，不把 reasoning_content 当作答案）。"""
    try:
        msg = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(msg, dict):
        return None
    text = msg.get("content") or ""
    if not isinstance(text, str):
        return None
    text = text.strip()
    return text or None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="调用视觉模型识别图片（自动故障切换）")
    parser.add_argument("--images", nargs="+", required=True, help="图片路径、URL 或 data URI，可传多个")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="要问图片的问题，默认是详细描述")
    parser.add_argument("--system", default=None, help="可选的系统提示词")
    parser.add_argument("--max-tokens", type=int, default=2048, help="最大输出 token 数")
    parser.add_argument("--temperature", type=float, default=0.3, help="采样温度，默认较低以保证 OCR 准确")
    parser.add_argument("--model", default=None, help="只使用指定模型（格式: 提供商/模型名 或 模型名，默认提供商 zhipu）")
    args = parser.parse_args()
    if args.max_tokens <= 0 or not 0 <= args.temperature <= 2:
        parser.error("max-tokens 必须大于 0，temperature 必须在 0 到 2 之间")


    # 确定本次要试的模型链
    if args.model:
        provider, _, model = args.model.partition("/")
        if not model:
            provider, model = "zhipu", args.model
        if provider not in PROVIDERS:
            parser.error("未知提供商: " + provider)
        # 若该模型在默认链里有元数据（max_out/max_images），直接复用
        entry = next((e for e in MODEL_CHAIN if e["provider"] == provider and e["model"] == model), {})
        chain = [{"provider": provider, "model": model,
                  "max_out": entry.get("max_out", 1 << 30),
                  "max_images": entry.get("max_images")}]
    else:
        chain = list(MODEL_CHAIN)

    # 预检图片源是否合法（存在/非目录），全部合法才继续
    for img in args.images:
        if img.startswith("data:") or img.startswith("http://") or img.startswith("https://"):
            continue
        if not os.path.exists(img):
            sys.stderr.write("错误: 文件不存在: %s\n" % img)
            sys.exit(2)
        if os.path.isdir(img):
            sys.stderr.write("错误: 这是目录而不是图片文件: %s\n" % img)
            sys.exit(2)

    auth_failed = set()     # Key 无效的提供商，跳过其全部模型
    no_key_reported = set()  # 已提示过缺 Key 的提供商
    errors = []

    for entry in chain:
        p = entry["provider"]
        if p in auth_failed or p not in PROVIDERS:
            continue
        key = get_api_key(p)
        if not key:
            if p not in no_key_reported:
                sys.stderr.write("提供商 %s 未配置 API Key，跳过其模型\n" % p)
                no_key_reported.add(p)
            continue
        if entry.get("max_images") and len(args.images) > entry["max_images"]:
            sys.stderr.write("%s/%s 只支持单张图，跳过（本次 %d 张）\n" % (p, entry["model"], len(args.images)))
            continue

        max_tokens = min(args.max_tokens, entry["max_out"])
        if max_tokens != args.max_tokens:
            sys.stderr.write("%s/%s 最大输出 %d tokens，已自动截断\n" % (p, entry["model"], max_tokens))

        # 图片按提供商要求编码（智谱裸 base64，硅基流动加 data URI 前缀）
        content = []
        for img in args.images:
            part = build_image_part(img, p)
            if part is None:
                sys.exit(2)
            content.append(part)
        content.append({"type": "text", "text": args.prompt})

        messages = []
        if args.system:
            messages.append({"role": "system", "content": args.system})
        messages.append({"role": "user", "content": content})

        payload = {
            "model": entry["model"],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": args.temperature,
            "stream": False,
        }

        for attempt in range(MAX_ATTEMPTS_PER_MODEL):
            data, err = call_api(p, key, payload)
            if err is None:
                text = extract_text(data)
                if text:
                    sys.stderr.write("识别成功，模型: %s/%s\n" % (p, entry["model"]))
                    print(text)
                    return 0
                errors.append("%s/%s: 模型未返回文本内容" % (p, entry["model"]))
                break
            errors.append("%s/%s: %s" % (p, entry["model"], err["message"]))
            if err["kind"] == "auth":
                auth_failed.add(p)
                sys.stderr.write("提供商 %s 的 API Key 无效，跳过其全部模型\n" % p)
                break
            if err["kind"] == "overload":
                sys.stderr.write("%s/%s 过载被限流，切换下一个模型\n" % (p, entry["model"]))
                break  # 过载是模型侧的，直接换下一个
            if err["kind"] == "bad_request":
                break  # 请求/模型本身不可用，重试没有意义
            # transient / network: 重试后再换下一个模型
            if attempt < MAX_ATTEMPTS_PER_MODEL - 1:
                sys.stderr.write("%s/%s 临时故障，3 秒后重试\n" % (p, entry["model"]))
                time.sleep(3)

    # 全部模型都失败
    if not errors:
        sys.stderr.write("错误: 没有可用的视觉模型（未配置任何 API Key，或所有模型均被跳过）\n")
    else:
        sys.stderr.write("错误: 所有 %d 个视觉模型均失败:\n" % len(errors))
        for e in errors:
            sys.stderr.write("  - %s\n" % e)
    sys.exit(1)


if __name__ == "__main__":
    main()
