# Lemqo 官网

中英双语静态网站，面向 `https://lemqo.com`，可部署到 Cloudflare Pages。

正式网址：[Lemqo.com](https://lemqo.com/)，[English](https://lemqo.com/en/)。
已部署到 Cloudflare Pages 免费项目 `lemqo`，域名已激活并启用 HTTPS。
备用网址：[lemqo.pages.dev](https://lemqo.pages.dev/)。完整验证记录见 [VALIDATION.md](VALIDATION.md)，部署与 DNS 状态保存在 `deployment/`。

- 中文：`/`
- English：`/en/`
- 响应式布局、手机导航、中英文切换。
- 理念、推理体系、当前进展、路线图与开源参与入口。
- 浏览器证明实验室：三个来自现有仓库的真实示例，可以验证、篡改、查看并下载证书。
- 搜索引擎元信息、语言链接、网站地图、分享图片、404 与响应头。
- 没有前端依赖、远程字体、统计脚本或外部服务请求；中文开源字体在本站提供。

网站将自主数学体系明确描述为长期愿景；当前进展依据仓库的 v0.2 文档及验证记录。

## 本地预览

需要 Node.js 20 或更高版本，无须安装依赖。在 `website` 目录运行：

```text
node build.mjs
node preview.mjs
```

打开 `http://127.0.0.1:4173`，英文页面为 `http://127.0.0.1:4173/en/`。
`LEMQO_PREVIEW_PORT` 可以指定其他端口。

## 内容与维护

| 内容 | 文件 |
| --- | --- |
| 中英文文案 | `src/content.mjs` |
| 页面布局与推理图 | `src/template.mjs` |
| 样式与响应式布局 | `src/styles.css` |
| 证明实验室及导航交互 | `src/app.mjs` |
| 浏览器演示验证器 | `src/checker.mjs` |
| 分享图片与图标 | `src/social-card.png`、`src/favicon.svg` |

`build.mjs` 从仓库 `examples/` 读取示例，检查后复制到静态发布目录。更新内容后重新构建。
演示验证器用于内存中的预设示例，覆盖十条 IPL 规则与目标/前提绑定；它不接收任意上传文件，不替代 Python CLI 的严格字节级解析、完整资源政策或发布验证。

验证命令（需要仓库原有的 Python 3.11+）：

```text
node --test tests/checker.test.mjs
```

测试将演示结果与 Python CLI 对全部原有示例的检查结果比较，并检查篡改、目标绑定、未使用节点、假设解除、别名与资源边界。

## 部署到 Cloudflare Pages

当前项目使用 Direct Upload。更新网站时重新构建，在现有 `lemqo` 项目创建新的生产部署并上传 `dist` 或 ZIP；当前没有启用 Git 自动部署。

两种方式都可使用。希望以后推送代码后自动更新网站，选择 Git 集成；希望先快速上线，使用现成发布包。

### 方式 A：Git 集成，适合长期维护

把 `website/` 源码推送到这个项目的 GitHub 仓库，在 Cloudflare 控制台新建 **Pages** 项目并连接仓库，配置：

| 设置 | 值 |
| --- | --- |
| Production branch | 你的实际生产分支，以推送网站源码后的 GitHub 分支为准 |
| Framework preset | None |
| Root directory | `website` |
| Build command | `node build.mjs` |
| Build output directory | `dist` |
| Environment variable | `NODE_VERSION=22` |

保留仓库根目录 `examples/`：构建时会读取其中的真实证明示例。Cloudflare 克隆完整仓库，只把构建工作目录设为 `website`。

### 方式 B：上传发布包，适合首次快速上线

1. 本地运行 `node build.mjs`，或使用已生成的 `lemqo-cloudflare.zip`。
2. 在 Cloudflare 控制台进入 **Workers & Pages**，新建 **Pages**，选择文件上传（Direct Upload）。
3. 项目名称可用 `lemqo`；如果已被占用，选择另一个可用名称。
4. 上传 `dist` 文件夹或发布 ZIP。ZIP 根目录直接包含 `index.html`、`en/`、`assets/`、`_headers` 等文件。
5. 部署成功后先打开 Cloudflare 返回的 `*.pages.dev` 地址，检查首页、语言切换和证明实验室。

Direct Upload 项目以后无法原地改成 Git 集成；要改用 Git，需要建立新的 Pages 项目。

官方参考：[Pages Git 集成](https://developers.cloudflare.com/pages/get-started/git-integration/)、[Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/)。

## 阿里云域名接入 Lemqo.com

域名可以继续在阿里云注册和续费。使用 Cloudflare Pages 托管根域名 `lemqo.com` 时，需要把该域名的权威 DNS 接入同一 Cloudflare 账号。

1. 在 Cloudflare 添加 `lemqo.com`，选择适合你的计划，记下它实际分配的两条 nameserver 地址。
2. 检查并补全 Cloudflare 中已有的 DNS 记录；如果域名用于邮箱，保留 MX、SPF、DKIM、DMARC 等记录。已启用 DNSSEC 时，按阿里云与 Cloudflare 的迁移说明处理原有 DS 记录。
3. 在阿里云的**域名控制台 → lemqo.com → 管理 → DNS 修改**，把 DNS 服务器改为 Cloudflare 实际分配的两条地址。不要填写示例地址，也不要混用阿里云和 Cloudflare 的 nameserver。
4. 等待 Cloudflare 中域名状态变为 Active。
5. 打开 Pages 项目 → **Custom domains → Set up a domain**，添加 `lemqo.com`。Pages 会引导创建对应的 DNS 记录和 HTTPS 证书。
6. 如需支持 `www.lemqo.com`，同样把它添加为自定义域名。可按官方说明，把 `www` 重定向到 `https://lemqo.com` 并保留路径、查询参数。
7. 等待自定义域名与证书都显示 Active，再检查 `https://lemqo.com` 与 `https://lemqo.com/en/`。

若只需要 `www.lemqo.com` 等子域名，可保留阿里云 DNS，先在 Pages 绑定该子域名，再到阿里云添加指向实际 `*.pages.dev` 地址的 CNAME。直接使用根域名 `lemqo.com` 的方案按上面的 DNS 接入步骤操作。

官方参考：[Cloudflare Pages 自定义域名](https://developers.cloudflare.com/pages/configuration/custom-domains/)、[阿里云修改 DNS 服务器](https://help.aliyun.com/zh/dws/user-guide/modify-dns-server)、[www 重定向](https://developers.cloudflare.com/pages/how-to/www-redirect/)。

## 上线检查

- `/` 显示中文，`/en/` 显示英文，切换后保留当前章节。
- 三个证明示例正常通过；篡改最后一步后被拒绝；更换示例会重置状态。
- 下载的命题与证书可使用 `python -m lemqo check PROOF --claim CLAIM` 检查。
- 手机上导航可展开/关闭，证明表格可横向浏览。
- GitHub、文档、贡献指南与验证记录链接正常。
- 不存在的路径返回 404。

## 授权

网站代码和原创标识沿用仓库的 MIT License。
自带的 Noto Sans SC / Noto Serif SC 字体采用 SIL Open Font License 1.1，授权文件位于 `src/fonts/`。
字体按现有文案做了子集处理；如果新增中文字未被覆盖，会回退到系统字体。需要重新生成子集时，可运行 `node tools/prepare_fonts.mjs`（仅此资产准备步骤需要网络）。
