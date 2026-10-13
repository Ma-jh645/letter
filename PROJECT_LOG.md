# 异地情侣信件 App — 项目日志

> 一句话：写给女朋友的远程投递信件 App。写信 → 定时投送 → 对方手机弹窗 → 信封动画 → 没看就留在桌面。
> 设备：她是荣耀（MagicOS，无 GMS），我是 vivo V2241A（Android 16 / API 36）。
> 代码位置：`D:\daima\letter-app\`
> 最后更新：2026-10-14

---

## 这个文档怎么用

1. **每次坐下来写代码，先看下面「现在做到哪了」。** 隔三周不碰也能一分钟捡回来。
2. **每次收工前，往最底下「日志」里追加一条。** 哪怕只有三行。
3. 格式不重要，**写完才是重点**。实在没话说就写三件事：今天做了啥、卡在哪、下次从哪开始。

---

## 现在做到哪了

**当前阶段：阶段 1 已完成，下一步是阶段 2（接数据库）。**

- ✅ 阶段 0：开发环境全部装好并验证过
- ✅ 阶段 1：后端骨架跑通，`http://127.0.0.1:8000/docs` 能看到 health 接口
- ✅ 代码已提交 git（1 个提交：「阶段1: FastAPI 骨架 + health 接口」）
- ⬜ **下一步 → 阶段 2：接 Postgres 数据库**
- ⬜ Android 端一行代码都还没写
- ⬜ 每个接口的埋点还没设计

**下次开工的第一件事（15 分钟热身，先确认环境还活着）：**

```powershell
cd D:\daima\letter-app\backend
uv run uvicorn app.main:app --reload
```

浏览器打开 http://127.0.0.1:8000/docs ，看到 `health` 接口就说明一切正常，可以往下做了。

> 如果 `/docs` 白屏：那是 Swagger UI 的界面文件从国外 CDN 加载失败，不影响后端，先访问 http://127.0.0.1:8000/openapi.json 确认真在跑。

---

## 剩余路线图

> 早先说过「阶段 1B」，就是现在的阶段 2，改个编号而已。

### 阶段 2 · 接数据库 ← 现在这里

**目标：** 让后端能存住东西。现在它一重启就失忆。

1. 注册 [Neon](https://neon.tech) 免费账号，建 Postgres 项目，区域选 Singapore / AWS Asia Pacific
2. 拿到连接串，填进 `.env` 的 `DATABASE_URL`，**记得把 `postgresql://` 改成 `postgresql+asyncpg://`**
3. 写 `app/db/session.py`：async engine + session 工厂
4. 初始化 Alembic，把 `env.py` 改成能读 `.env`、能自动发现模型（这是新手最耗时的坑）
5. 建第一张表，跑通第一次迁移

**做完的标志：** `alembic upgrade head` 成功，数据库里能看到你建的表。

### 阶段 3 · 数据模型 + 核心接口

**目标：** 后端能真正处理「用户」和「信件」。

1. 设计表：用户、信件（内容/图片/收件人/投递时间/状态）
2. 顺手建**埋点事件表**（见下方「数据方向备注」，这张表越早设计越省事）
3. 写注册/登录接口，签发 JWT
4. 写信、存草稿、查列表、查详情这些接口
5. 图片走 Cloudflare R2 预签名直传

**做完的标志：** 在 `/docs` 里能完成「注册 → 登录 → 写一封信 → 查出来」整套流程。

### 阶段 4 · 定时投递

**目标：** 信能到点自己送出去。

1. 接 APScheduler，定期扫描「已到投递时间」的信
2. 状态机：草稿 → 待投递 → 已投递 → 已查看
3. 处理服务器重启后漏送的补投

**做完的标志：** 设一封信 5 分钟后投递，到点数据库状态自动变。

### 阶段 5 · 实时推送（WebSocket）

**目标：** 信一投出去，对方手机立刻知道。这是能不能取代「手动刷新」的关键。

1. 后端开 WebSocket 接口，维护在线连接
2. 投递时向收件人的连接推一条消息
3. 处理断线重连、心跳

**做完的标志：** 两个终端连同一个服务，一个触发投递，另一个立刻收到消息。

### 阶段 6 · Android 骨架

**目标：** 手机上能跑起来、能登录、能写信。

1. Android Studio 建项目，`minSdk 26 / targetSdk 36`，Kotlin + Jetpack Compose
2. 分层：MVVM + Repository；本地用 Room，网络用 Retrofit
3. 登录页、信件列表页、写信页
4. 连本地后端调试（真机连电脑要用局域网 IP，不是 127.0.0.1）

**做完的标志：** 真机上能注册登录，写一封信成功存进服务器。

### 阶段 7 · 后台保活 + 通知

**目标：** App 在后台也能收到信，且弹窗看得见。

1. 前台服务维持 WebSocket 长连接（无 GMS，FCM 完全不可用，只能自己扛）
2. 通知**必须分渠道**：投递通知走高优先级，常驻通知走低优先级，混用会一直响
3. Android 14+ 前台服务要在 manifest 声明 `foregroundServiceType`
4. 荣耀 / vivo 的后台管控很激进，要做保活引导页（自启动、电池白名单、后台高耗电、最近任务加锁、悬浮窗权限）

**做完的标志：** App 切后台、锁屏一段时间后，信投递过来仍然能弹窗。

### 阶段 8 · 可爱层

**目标：** 让它可爱到愿意一直用。这一步不是锦上添花，是这个产品能不能活下来的关键。

1. 收信时的信封打开动画
2. 桌面元素：Glance 小组件 + `TYPE_APPLICATION_OVERLAY` 悬浮窗 + 常驻通知，三选一或组合，实现「没看就留在桌面」
3. 信纸样式、字体、贴纸、自定义称呼
4. 悬浮窗权限被拒要有降级路径（退回常驻通知 + 角标）

**做完的标志：** 她自己愿意截图发朋友圈。

### 阶段 9 · 稳定化 + 真机联调

**目标：** 从「能跑」变成「敢用」。

1. 断网、切后台、重启、权限被拒，逐项测
2. 前台服务 + 长连接 + 悬浮窗很费电，加「夜间静默」开关
3. 打 APK 直接发给她装（两人自用不需要任何开发者账号）

**做完的标志：** 能连着用两周不出问题。

---

## 环境清单

> 换电脑或重装系统时照这个装。全部于 2026-09-23 装好并验证过。

| 组件 | 版本 | 位置 |
|---|---|---|
| Python | 3.13.5 | `D:\ANA\python.exe` |
| uv | 0.12.18 | `D:\ANA\Scripts\uv.exe`（已在 PATH） |
| JDK | 17.0.18 | `D:\JDK_of_java\jdk17`（`JAVA_HOME` 已设 Machine 级） |
| Node | v24.16.0 | |
| Git | 2.51.0 | `D:\PortableGit\bin\git.exe` |
| Android Studio | — | `D:\Android` |
| PyCharm | 2025.3.3 Pro | `D:\Python\PyCharm 2025.3.3` |
| Android SDK | — | `C:\Users\12315\AppData\Local\Android\Sdk` |

SDK 内部装了：platform-tools 37.0.1、platforms `android-36` + `android-37`、build-tools 36.0.0 + 37.0.0、sources `android-36`、cmdline-tools latest 23.0.0。

**故意没装的：** 模拟器（用真机调试）、Docker Desktop（数据库用云托管）。

**环境变量：** `ANDROID_HOME` 和 `ANDROID_SDK_ROOT` 已设用户级；PATH 已追加。

**坑：** `sdkmanager` 已经废弃，现在用 `android.exe sdk install <包名>`，包名写斜杠形式（如 `platforms/android-36`）。安装时要喂 `y` 接受许可。

---

## 技术选型（以及为什么）

| 项 | 选择 | 为什么 |
|---|---|---|
| 平台 | 只做 Android | 你俩都是安卓，iOS 直接放弃，省一台 Mac + 999/年 |
| 后端 | FastAPI + SQLAlchemy async + asyncpg | 你本来就会 FastAPI |
| 数据库 | Postgres（Neon 免费托管） | 不装 Docker，两个人用免费额度绰绰有余 |
| 定时任务 | APScheduler | 轻量，够用 |
| Android | Kotlin + Jetpack Compose + MVVM | 官方推荐路线 |
| 本地存储 | Room | |
| 网络 | Retrofit + WebSocket | |
| 桌面元素 | Glance 小组件 + 悬浮窗 + 常驻通知 | 三个都上，互为备份 |
| 推送 | 自建 WebSocket 长连接 | **无 GMS，FCM 不可用**，只能自己保活 |
| 图片 | Cloudflare R2 预签名直传 | 省服务器带宽 |
| 分发 | 直发 APK | 两人自用，不需要开发者账号 |
| 成本 | 约 ¥500–800/年 | 无一次性支出 |

---

## 数据方向备注

> 目标是找数据科学 / 数据分析实习。这个项目本身不提供「数据科学」的说服力（两个人、数据量太小，做不了统计推断），但能真实证明**数据管道 + 指标体系 + 决策闭环**的能力。
>
> 所以阶段 3 建表时，把埋点事件表一起设计进去——这时候做几乎零成本，等功能都做完再补埋点会痛苦十倍。

事件表大致长这样：`user_id / event_name / event_time / letter_id / 设备信息`

要埋的事件：`letter_created`、`letter_delivered`、`letter_opened`、`widget_dismissed` 等。

后续这个方向要做出的东西：

- 一份**指标字典**（北极星指标、开口率、投递成功率、未读留存时长……）——本质是文档，体现的是「知道该看什么」
- 一条 **ETL**（原始事件表 → SQL 聚合 → 日/周汇总表）
- 一个**看板**（建议 Streamlit，纯 Python，不用 Docker）
- 一份**闭环报告**（发现 → 改动 → 改动后对比），这个最值钱

另外记住：这些**替代不了 SQL 和统计基础**。笔试题就是写 SQL，面试就是问留存/漏斗/AB 测试/辛普森悖论。那是另一条并行的线。

---

## 已完成的部分（详细存档）

### 阶段 0 · 环境搭建 ✅

装了 Python、uv、JDK 17、Node、Git、Android Studio、PyCharm 和整套 Android SDK，配好环境变量，真机 `adb devices` 能识别。

顺手修了一个坑：Android Studio 的代理配置里有个 PAC 项和死端口 `127.0.0.1:7890`，清掉了。

### 阶段 1 · 后端骨架 ✅

工程位置 `D:\daima\letter-app\backend`。

**目录结构：**

```
backend/
├─ .env                    配置（含 JWT_SECRET，不进 git）
├─ pyproject.toml
├─ uv.lock
├─ .gitignore
└─ app/
   ├─ main.py              入口，装配路由
   ├─ core/config.py       配置中心，从 .env 读
   ├─ api/routes/health.py 第一个接口
   ├─ db/                  （空的，阶段 2 填）
   ├─ models/              （空的，阶段 3 填）
   └─ schemas/             （空的，阶段 3 填）
```

**已装依赖：** fastapi 0.141.1、uvicorn 0.53.0、pydantic-settings 2.15.0、sqlalchemy 2.0.54、asyncpg 0.31.0、alembic 1.20.0。

**验证过：** `GET /api/health` 返回 `{"status":"ok"}`，`GET /docs` 返回 200。

**启动命令（必须在 `backend` 目录下敲）：**

```powershell
uv run uvicorn app.main:app --reload
```

三层分工别忘：**uv 管环境 → uvicorn 管网络 → FastAPI 管逻辑**。

---

## 踩过的坑（持续累积）

1. **`uv init` 新版默认 src 布局**，会生成 `src/letter_backend/` 而不是 `main.py`，还会把项目自己当库打包安装。修法：删 `src/`，删 `pyproject.toml` 里的 `[project.scripts]` 和 `[build-system]`，加 `[tool.uv] package = false`，再 `uv sync`。
2. **`.gitignore` 一开始没排除 `.env`**，密钥差点被提交。已补上 `.env`、`.idea/`、`.vscode/`。
3. **uv 硬链接失败警告**（缓存在 C 盘、项目在 D 盘，跨盘不支持硬链接）。无害，想消掉就设环境变量 `UV_LINK_MODE=copy`。
4. **`/docs` 白屏**是因为 Swagger UI 的静态文件默认从国外 CDN 加载。后端没问题，看 `/openapi.json` 就知道。国内网络下想稳定用可以换镜像。
5. **Alembic 的 `env.py` 默认不读 `.env`、也不会自动发现模型**，必须手动改，否则迁移会生成空表。阶段 2 会碰到。
6. **荣耀推的不是华为 HMS**，网上华为 Push Kit 的教程不适用。而且国内荣耀 / vivo 都没有 GMS，**FCM 完全不可用**。
7. **通知必须分渠道**，投递通知高优先级、常驻通知低优先级，混用会一直响。
8. **Android 14+ 前台服务**必须在 manifest 声明 `foregroundServiceType`（用 `specialUse`）。

---

## 日志

> 新的写最上面。三行也行。

### 2026-10-14

- 隔了三周回来，什么都忘了。建了这份文档，把已完成的部分和剩余路线图都记下来。
- 确认环境完好：uv 0.12.18、Python 3.13.5、JDK 17.0.18、Node v24.16.0、Git 2.51.0，Android SDK 都在。
- 把 git 仓库根从 `backend/` 提升到 `letter-app/`，这样这份日志和以后的 `android/` 都在同一个仓库里。提交：`b3663f3`。
- 下一步：阶段 2，接数据库。

### 2026-09-23

- 阶段 0 完成：环境全部装好。
- 阶段 1 完成：后端骨架跑通，health 接口验证通过。
- 提交 git：`a96697e 阶段1: FastAPI 骨架 + health 接口`
