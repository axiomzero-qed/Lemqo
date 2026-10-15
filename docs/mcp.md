# MCP stdio reference server / MCP stdio 参考服务

Run with Python 3.11+, without installing packages:

使用 Python 3.11+，无需安装软件包：

```sh
python -m lemqo mcp --ipl-claim examples/identity.claim.json
```

The operator chooses trusted inputs at startup. Tool calls cannot change the
claim, reference, permitted axioms, executable paths, proof root or timeout.
`verify_ipl_proof` accepts one `proof` string containing certificate JSON and
calls the existing `verify_bytes` API. To additionally expose
`verify_lean_certificate`, supply all four Lean options:

操作者在启动时选择可信输入。工具调用不能修改 claim、参考导出、允许公理、可执行文件路径、证明根目录或时限。`verify_ipl_proof` 接收一个包含证书 JSON 的 `proof` 字符串，直接调用现有 `verify_bytes` API。如需同时暴露 `verify_lean_certificate`，须提供全部四个 Lean 选项：

```sh
python -m lemqo mcp --ipl-claim examples/identity.claim.json \
  --lean-claim /tmp/certificates/claim.json \
  --reference /tmp/certificates/reference.ndjson \
  --backends /tmp/lemqo-backends/backends.json \
  --proof-root /tmp/submitted-proofs --timeout 7200
```

The Lean tool accepts only a relative `proof_path` beneath `--proof-root`;
absolute paths, traversal and symlink escapes are rejected. It calls the same
`verify_lean_files` API. This tool requires the prepared native backends on the
validated Linux/WSL platform. You may omit IPL options for a Lean-only server.
Use a directory dedicated to submitted proof data and protect the trusted
configuration from modification by the proof producer.

Lean 工具只接受 `--proof-root` 下相对的 `proof_path`；绝对路径、路径穿越及符号链接逃逸均被拒绝。它调用相同的 `verify_lean_files` API，需要在已验证的 Linux/WSL 平台上准备原生后端。仅需要 Lean 工具时可省略 IPL 选项。应使用专门存放证明数据的目录，并保护可信配置，避免证明生成方修改。

Example client configuration; replace Python and working-directory paths with
the actual local paths, or use an absolute release `.pyz` in the arguments:

客户端配置示例；须将 Python 及工作目录替换为真实本地路径，也可在参数中使用发布 `.pyz` 的绝对路径：

```json
{
  "mcpServers": {
    "lemqo": {
      "command": "python",
      "args": ["-m", "lemqo", "mcp", "--ipl-claim", "/absolute/Lemqo/examples/identity.claim.json"],
      "cwd": "/absolute/Lemqo"
    }
  }
}
```

The reference implementation follows the MCP
[stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports),
[lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)
and [tool interface](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).
It supports versions `2025-11-25`, `2025-06-18`, `2025-03-26`, initialization,
`ping`, `tools/list`, and `tools/call`. UTF-8 JSON-RPC messages occupy one line,
are limited to 8 MiB, and reject duplicate keys and nonfinite numbers. Stdout
contains protocol messages only. Rejections return `isError: true` with the
original rejection code; internal errors never become successful receipts.

参考实现遵循 MCP 的 [stdio 传输](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)、[生命周期](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)及[工具接口](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)。支持上述三个协议版本、初始化、`ping`、`tools/list` 和 `tools/call`。UTF-8 JSON-RPC 消息每条占一行，上限 8 MiB，拒绝重复键及非有限数。Stdout 仅包含协议消息。拒绝返回 `isError: true` 和原始拒绝码；内部错误不会变成成功回执。

This is a small, sequential local reference server. It has no HTTP listener,
authentication service, parallel jobs, resumable transport or in-flight
cancellation. A long Lean check occupies the session until it finishes or
times out; batch production should use the [phase CLI](batch.md). Clients may
need longer request timeouts. Connecting a verifier does not grant a model the
right to select its own trust policy or establish the intended meaning of a
mathematical statement.

这是小型串行本地参考服务，不含 HTTP 监听、认证服务、并行作业、可恢复传输或执行中取消。长时间 Lean 检查会占用会话直到完成或超时；批量任务应使用[分阶段 CLI](batch.md)，客户端也可能需要更长请求时限。接入验证器不表示模型可以选择自己的信任策略，也不确立数学陈述的预期含义。
