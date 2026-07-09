# StudyPlayer iPhone 使用指南

这份文档只覆盖最小可用流程：Mac 生成 `.study`，Xcode 安装 App，iPhone 导入学习包并离线学习。

## 1. 准备条件

Mac：

```text
已安装 Xcode
Xcode 已登录 Apple Account
study-media 项目在 /Users/zhaoxin/workspace/study/study_project
```

iPhone：

```text
已用数据线连接 Mac
已信任这台 Mac
已开启 Developer Mode
```

如果命令行还没有指向 Xcode，执行一次：

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

验证：

```bash
xcodebuild -version
```

## 2. 生成学习包

```bash
conda activate study_media
cd /Users/zhaoxin/workspace/study/study_project

study-media process /Users/zhaoxin/workspace/study/courses/3Blue1Brown/Entropy-Compression.mp4
study-media package 3Blue1Brown/Entropy-Compression
```

输出：

```text
/Users/zhaoxin/workspace/study/study_project/iphone_export/packages/3Blue1Brown/Entropy-Compression.study
```

以后日常只需要把 `.study` 传到 iPhone。

## 3. 用 Xcode 安装 App

打开工程：

```bash
open /Users/zhaoxin/workspace/study/study_project/ios/StudyPlayer/StudyPlayer.xcodeproj
```

在 Xcode 中：

```text
1. 左侧选择 StudyPlayer project
2. 选择 StudyPlayer target
3. 打开 Signing & Capabilities
4. 勾选 Automatically manage signing
5. Team 选择你的 Apple Account
6. Bundle Identifier 保持 com.zhaoxin.studyplayer
7. 顶部设备选择你的 iPhone
8. 点击 Run
```

如果 iPhone 提示 Developer Mode：

```text
Settings
  -> Privacy & Security
  -> Developer Mode
  -> On
```

然后按提示重启 iPhone，再回到 Xcode 点击 Run。

## 4. 把 .study 传到 iPhone

少量课程推荐 AirDrop：

```bash
open /Users/zhaoxin/workspace/study/study_project/iphone_export/packages/3Blue1Brown
```

在 Finder 中右键：

```text
Entropy-Compression.study
  -> Share
  -> AirDrop
  -> 选择你的 iPhone
```

iPhone 上如果出现打开方式，优先选：

```text
StudyPlayer
```

如果只保存到 Files，建议保存到：

```text
On My iPhone/
  StudyMedia/
    Inbox/
      Entropy-Compression.study
```

## 5. 在 iPhone 导入

打开 `StudyPlayer`：

```text
1. 点右上角导入按钮
2. Browse
3. 进入 On My iPhone/StudyMedia/Inbox
4. 选择 Entropy-Compression.study
5. 等待提示“已导入”
```

导入后课程会出现在首页列表。

## 6. 学习操作

进入课程后：

```text
播放 / 暂停：点顶部按钮
拖动进度：用顶部滑条
跳转：点击任意一句 transcript
自动高亮：播放时当前句子会高亮
保存进度：退出页面时自动保存
删除课程：课程列表左滑删除
```

导入完成后，Files 里的 `.study` 原文件可以删除，因为 App 已经复制了一份到自己的本地空间。

## 7. 常见问题

### Xcode 提示没有 Team

确认：

```text
Xcode
  -> Settings
  -> Accounts
```

里面已经添加 Apple Account。

### Xcode 提示 Bundle Identifier 冲突

把 Bundle Identifier 改成更唯一的名字，例如：

```text
com.zhaoxin.studyplayer.local
```

### App 看不到 .study 文件

确认 `.study` 保存在：

```text
On My iPhone/StudyMedia/Inbox
```

然后在 StudyPlayer 里点导入，选择 Browse。

### 导入失败

先在 Mac 重新打包：

```bash
study-media package 3Blue1Brown/Entropy-Compression
```

再 AirDrop 新的 `.study`。

### 免费 Apple Account 需要重新安装

如果过一段时间 App 打不开，用 Xcode 重新 Run 一次即可。这个项目是个人使用，不需要上架 App Store。

