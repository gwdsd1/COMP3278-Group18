# COMP3278 Group 18 · 项目交接

更新于 **2026 年 11 月 17 日**。课程提交截止为 **2026 年 12 月 2 日 23:59（香港时间）**，如有更新以 Moodle 通知为准。

**当前进度：程序和数据已可演示。** Q1–Q9 共 9 个功能，其中 Q3–Q9 共 7 个高级功能，达到课程至少 8 个功能、4 个高级功能的门槛。接下来优先完成正式 ER 图、报告、视频和最终提交包。

- [在线演示](https://gwdsd1.github.io/COMP3278-Group18/)：浏览器直接运行 SQLite，打开即可试用。
- [GitHub 仓库](https://github.com/gwdsd1/COMP3278-Group18)：`main` 是协作分支，也是课程离线版代码所在位置。`gh-pages` 存放线上演示的构建产物。
- [中英数据手册](CS2_Data_Guide_ZH_EN.md)：查赛事范围、字段定义、数据来源、覆盖情况和 Q1–Q9 SQL。

## 先跑一次项目

从 GitHub 克隆或下载仓库，在包含 `app/` 和 `database/` 的根目录运行：

```bash
python app/server.py
```

用 Python 3.10 或更新版本。部分系统命令是 `python3`。打开 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)，用完按 Ctrl+C 停止。如果端口被占用，运行 `python app/server.py --port 8001`。离线版使用 Python 标准库和已随仓库提供的 SQLite 文件。

**体验路径**：Q1 点 **Run query** → **IEM Beijing 2026** → 查看对局和选手榜 → 点决赛的 **View match** → 在 **Mirage、Dust2、Inferno** 之间切换。决赛为 **MOUZ 3:0 The MongolZ**，每张地图都应显示两队各 5 人的计分板。录视频也可以用这场。赛事 ID 是 `8245`，决赛的本地比赛 ID 是 `2400011`。

## 文件放在哪里

```text
COMP3278-Group18/
├── README.md                   启动说明和在线演示入口
├── TEAM_HANDOFF.md              本交接文档
├── CS2_Data_Guide_ZH_EN.md       数据手册、来源和查询说明
├── GP_Project_Proposal.md       初版方案与 ER 关系草稿
├── app/
│   ├── server.py                离线 Python 网页、表单和详情页
│   ├── queries.sql              Q1–Q9 和详情页所用 SQL
│   └── style.css                离线版与在线版共用样式
├── database/
│   ├── schema.sql               8 张表、主外键、约束和视图
│   ├── seed.sql                 赛事、比分和选手数据
│   ├── build.sql                课程提供的 SQLite 构建脚本
│   └── app.db                   两个版本都使用的 SQLite 快照
└── pages/
    ├── index.html、app.js       在线演示的入口和浏览器端代码
    └── build.py                 生成 GitHub Pages 构建产物
```

## 已经完成什么

数据库覆盖 **17 届赛事、36 个阶段、621 场系列赛、1,437 张已打地图、14,370 条选手逐图记录**。每张已打地图都有比分和双方各 5 人的 ADR、助攻等数据。所有系列赛都有开赛时间。数据库可以从 `schema.sql` 和 `seed.sql` 重建，现有快照已通过完整性及外键检查。

| 编号 | 用户能查询什么 | 报告里可解释的 SQL 点 |
|---|---|---|
| Q1 | 按日期范围、最低奖金查赛事，结果可点进赛事详情 | 单表筛选，日期区间重叠 |
| Q2 | 查战队最近一次录得的阵容 | 按战队筛选阵容视图 |
| Q3 | 查赛事的开赛时间、阶段、对阵和赛果，结果可点进比赛详情 | JOIN，阶段优先显示数字轮次，再用签表标签 |
| Q4 | 查一场系列赛的逐图比分与胜者 | JOIN，按地图顺序排序 |
| Q5 | 查两队历史交手次数、胜场和胜率 | JOIN、聚合，处理双方位置互换 |
| Q6 | 查战队在各地图的胜率，可限制最低场次 | JOIN、GROUP BY、HAVING |
| Q7 | 查某届赛事的选手榜、K/D、助攻和加权 ADR | JOIN、分组聚合、HAVING |
| Q8 | 查选定期间内没有指定地图记录的战队 | `NOT EXISTS` |
| Q9 | 查一场比赛某张图的双方选手计分板 | JOIN，绑定比赛 ID 与地图 ID |

赛事详情复用 Q3 和 Q7，比赛详情复用 Q4，并通过地图链接切换 Q9。**离线版和线上版都在 Edge 验证过 Q1–Q9 及赛事到计分板的点击流程。** Q2 的阵容是历史样本，Q8 的结论限于本快照。Q7 的估算总伤害按逐图 `ADR × 回合数` 求和，精确总伤害仍为 `NULL`。录像、投掷次数和部分阶段标签有缺值，第一版按数据手册的口径展示。

## 接下来要做

| 优先级 | 任务 | 完成标准 |
|---|---|---|
| 1 | 确认 Moodle 组别和分工 | 三人在同一个 Group 18，确定报告负责人、录制安排和最终上传人。以下分工是建议，报告按实际贡献填写。 |
| 1 | 画正式 ER 图 | 按课堂记号画出 Event、Stage、Team、Player、Match、Map 6 个实体集，标清主键、基数和参与约束。解释 Match 的双方战队角色，并核对 `match_maps` 与 `player_map_stats` 的复合键和外键。 |
| 1 | 写并导出报告 | 从 Moodle 的 starter kit 取 `report_template.docx`，交 `report.pdf`，**含封面最多 5 页**。包括全员姓名学号、功能列表、ER 图及设计解释、逐功能的操作与 SQL／所用表／高级点、实际分工及 AI 使用说明。说明 `maps` 的 8 行是快照的固定地图目录。 |
| 1 | 补离线版提交文件 | 补 `requirements.txt`，注明仅用标准库，在 README 写明安装与启动方式。按课程 Windows 说明准备 `sqlite3.exe`。最终核对功能 SQL、表单选项和辅助查询的组织符合自写程序要求。 |
| 2 | 录制演示视频 | **最多 5 分钟，三人都发言**。选至少 2 个功能、其中至少 1 个高级。建议演示 Q1 和 Q9，一次走完整条路径。展示结果后，讲查询用了哪些表、如何连接和筛选，再用 SQLite 的 SELECT 给出产生结果的底层记录。 |
| 2 | 最终打包验收 | 用课程 `build.sql` 从最终 SQL 重建，解压一份新 ZIP，按 README 启动并复查核心查询。包含离线代码、SQL、`app.db`、报告及视频或链接，提交为 `COMP3278_Project_<提交人学号>.zip`，由一人上传 Moodle。 |

目前仓库里还没有正式 ER 图、最终报告、视频或提交 ZIP。如果有人已在本地起草，请在组内确认进度。Moodle 的 ZIP 上限为 **100 MB**。视频可交 `video.mp4` 或 `video.mov`。超过 **90 MB** 时上传到 HKU OneDrive 或设为不公开列出的 YouTube 视频，再交 `video_link.txt`，用无痕窗口确认链接可访问。仓库是公开的，含学号的报告和正式提交包通过 Moodle 或小组私下共享。

**建议三人分工**：A 负责 ER 图、约束与 Q1–Q2。B 负责 Q3–Q5、Q9 和详情页演示。C 负责 Q6–Q8、统计口径与功能–SQL 表。三人交叉复核，确保每个人都能解释 ER 图、表和查询。评分为程序 **50%**、报告 **30%**、视频 **20%**。

## 后续怎么改

- 网页和数据库的修改从 `main` 拉取最新版后开始，有写入权限的组员可开分支和 Pull Request，合并前让另一位组员复查。
- 改查询时以 [`app/queries.sql`](app/queries.sql) 为准，同步手册，先跑离线版再查看 Pages。改数据时同步 `seed.sql` 和生成的 `app.db`。在项目根目录用 `sqlite3 -bail :memory: ".read database/build.sql"` 重建。
- 线上演示与课程提交有不同的入口。只有网页、SQL 或数据库变动需要重建演示，按 [README](README.md) 生成产物后更新 `gh-pages`。报告和视频按离线 Python 应用演示与验收。
