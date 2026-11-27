# 王笑琨（Xiaokun Wang）的学术主页

北京科技大学王笑琨教授的个人主页，介绍个人经历、计算机图形学与交互技术研究、论文、科研项目、学术服务、获奖情况及 MultiFluid 专题。站点基于 al-folio 定制，使用 Jekyll 生成静态网页，通过 GitHub Pages 发布。[访问主页](https://xiaokun17.github.io/)

## 网站如何生成

构建时，Jekyll 读取全站配置和各页面开头的 YAML 配置块。配置块中的 `permalink` 决定页面网址，`layout` 指定包裹正文的模板。页面和模板都可以使用 Liquid 读取数据、遍历条目或插入公共组件。例如，同一份奖项数据可以在首页显示精选条目，在奖项页按类别完整展开。

Jekyll 将页面渲染为 HTML，将 Sass 编译为 CSS，并将结果和静态资源写入 `_site/`。浏览器加载生成的页面后，JavaScript 负责论文搜索、新闻展开和明暗主题切换等交互。修改内容或样式时，应编辑下表中的源文件，再重新构建。

| 代码位置 | 职责 |
| --- | --- |
| [全站配置](_config.yml) | 设置姓名、联系方式、站点地址、内容宽度、插件和功能开关。Ruby 构建依赖列在 [Gemfile](Gemfile) 中。 |
| [页面](_pages/) | 定义首页和各栏目页面。普通页面通过 `nav` 和 `nav_order` 控制是否出现在导航中及其顺序。 |
| [布局](_layouts/) 与 [公共组件](_includes/) | 布局定义整页或单条记录的结构。组件供不同页面复用，包括导航、页脚、图片和新闻列表。 |
| [结构化数据](_data/)、[文献库](_bibliography/) 与 [新闻](_news/) | 分别保存 YAML 数据、BibTeX 记录和逐条编写的新闻。模板在构建时读取这些内容。 |
| [构建插件](_plugins/) 与 [维护脚本](bin/) | Jekyll 自动加载 Ruby 插件，例如汇总论文年份。`bin/` 中另有论文导入、PDF 处理、预览图维护和部署脚本。 |
| [样式](_sass/) 与 [前端资源](assets/) | [Sass 入口](assets/css/main.scss) 汇总样式。[布局样式](_sass/_layout.scss) 包含首页、研究卡片和响应式规则，[基础样式](_sass/_base.scss) 包含论文列表样式，[主题样式](_sass/_themes.scss) 定义明暗配色。`assets/` 也保存 JavaScript、图片和 PDF。 |

## 首页如何组装

1. [首页内容](_pages/about.md) 将网址设为 `/`，指定 `about` 布局及头像文件。Biography 和 Research Interests 写在正文中，接着插入新闻列表，并从奖项数据中选出首页展示的条目。
2. [首页布局](_layouts/about.html) 在正文上方放置姓名、职称、单位、研究简介、头像和个人链接，在正文下方按配置显示精选论文与联系方式。修改履历时编辑首页正文，修改首屏的单位或一句话简介时编辑此布局。
3. [全站布局](_layouts/default.html) 包裹整个首页，载入导航、页脚和公共脚本。其他栏目大多使用[通用页面布局](_layouts/page.html)，并共享同一层全站布局。

## 一篇论文如何出现在网站上

1. 在[主文献库](_bibliography/papers.bib) 中添加一条 BibTeX 记录，填写标题、作者、四位年份等信息。本地 PDF 放入 [assets/pdf/](assets/pdf/)，缩略图放入 [assets/img/publication_preview/](assets/img/publication_preview/)，在记录的 `pdf` 和 `preview` 字段中填写对应文件名。
2. 构建时，[年份生成插件](_plugins/publication_years.rb) 从可见记录中提取年份并按降序排列。[论文页面](_pages/publications.md) 按年份调用 Jekyll Scholar 查询文献，由[单篇论文模板](_layouts/bib.html) 渲染作者、出处、缩略图和资源链接。新增年份会自动出现在列表中。有 DOI 的记录会显示独立的 DOI 按钮。
3. 首页的[精选论文组件](_includes/selected_papers.html) 从同一文献库选择 `featured = {true}` 的可见记录。`visible = {false}` 会同时从论文总表和首页精选中隐藏该条目。
4. 访客输入搜索词时，[论文交互脚本](assets/js/publications.js) 在已生成的条目中筛选匹配结果，并展开命中的年份。较早年份的分批显示范围由全站配置中的 `publication_year_cutoff` 和 `publication_year_batch_size` 控制。

## 其他栏目在哪里维护

| 栏目 | 内容来源与展示方式 |
| --- | --- |
| Research | [研究总览](_pages/research.md) 定义五张方向卡片，并链接到对应的 `_pages/research-*.md` 详情页。详情页的 `related_publications` 列表按 BibTeX key 引用可见论文，按列表顺序展示。首页的研究兴趣摘要单独维护在首页正文。 |
| News | 每条新闻是 [_news/](_news/) 下的一份 Markdown 文件。[新闻组件](_includes/news.html) 按日期倒序排列，供首页和[新闻页](news.html) 共用。`news_limit` 控制初始条数和每次展开的条数。 |
| Achievements | [奖项数据](_data/achievements.yml) 供两处使用。首页选取 `featured: true` 的条目，[完整列表](_includes/achievements.html) 按类别分组，并在每组内按年份倒序显示。 |
| Projects、Service、MultiFluid | 项目按负责人角色分组，清单直接写在 [Projects 页面](_pages/projects.md)。学术服务条目和 MultiFluid 图文分别维护在 [Service 页面](_pages/service.md) 和 [MultiFluid 页面](_pages/multifluid.md)。 |

仓库还保留了 al-folio 的[博客入口](blog/index.html)、[示例文章](_posts/)和 [CV 页面](_pages/cv.md)。[Members 页面](_pages/members.md) 从 [_projects/](_projects/) 集合生成卡片，与主导航中直接编写项目清单的 Projects 页面使用不同的数据来源。

## 本地预览与发布

### 构建并启动预览

启动 Docker Desktop，在包含 [docker-local.yml](docker-local.yml) 的项目根目录打开 PowerShell。首次运行或修改 `Dockerfile`、`Gemfile` 后，执行以下命令构建镜像并在后台启动容器：

```powershell
docker compose -f docker-local.yml up --build -d
```

容器启动后，Jekyll 读取 `_config.yml` 和 [_config_local.yml](_config_local.yml)，将网站生成到项目的 `_site/` 目录。首次生成完成后，打开[本地预览（localhost:8080）](http://localhost:8080/)。保存 Markdown、模板或样式文件后，Jekyll 会重新构建，浏览器会自动刷新。

如需查看生成进度或排查错误，运行 `docker compose -f docker-local.yml logs -f`。按 `Ctrl+C` 可退出日志查看，后台预览会继续运行。

### 停止预览

```powershell
docker compose -f docker-local.yml down
```

下次使用已有镜像启动预览时，运行 `docker compose -f docker-local.yml up -d`。

### 发布到 GitHub Pages

[GitHub Actions 工作流](.github/workflows/deploy.yml) 监听发往 `master` 或 `main` 的推送和拉取请求。推送时，[部署脚本](bin/deploy) 使用主配置执行生产构建，并将生成的静态文件推送到 `gh-pages` 分支。拉取请求也执行构建，使用 `--no-push` 跳过发布。

**暂停和恢复自动发布**

1. **关闭自动发布**。推送前打开仓库的 [Actions → deploy](https://github.com/xiaokun17/xiaokun17.github.io/actions/workflows/deploy.yml)，点击右上角的 `…`，选择 **Disable workflow**。暂停期间可以继续推送源码。关闭前已经启动的发布任务仍会继续运行。
2. **开启自动发布**。回到同一工作流页面，点击 **Enable workflow**。重新开启后，下一次向 `master` 或 `main` 推送新提交时，工作流会构建该分支的最新版本，一并发布暂停期间已经合入该分支的修改。

如果积累的修改已经推送，重新开启工作流后，打开 **Actions → deploy → Run workflow**，选择 `master`（或实际发布用的 `main`），再点击 **Run workflow**。构建成功后会更新 `gh-pages`。手动入口在包含该工作流的版本推送到 GitHub 默认分支后可用。

在 Actions 中还可以手动运行 **Prettify gh-pages** 格式化已发布的 HTML，或运行 **Docker Slim** 构建并验证瘦身镜像。勾选 `publish` 会将验证成功的镜像上传到此仓库的 GitHub Container Registry，标签为 `slim`。

## 主题与许可

本站基于 [al-folio](https://github.com/alshedivat/al-folio) 定制。上游主题采用 MIT 许可证，版权声明和许可条款见 [LICENSE](LICENSE)。
