# study-media

`study-media` 是一个个人学习媒体工具：在 Mac 上把课程视频处理成音频、文字和 `.study` 学习包，再用 iPhone 上的原生 `StudyPlayer` App 离线播放。

## 现在支持什么

Mac 端：

```bash
study-media process /path/to/video.mp4
study-media package /path/to/video.mp4
```

iPhone 端：

```text
StudyPlayer App
  导入 .study
  离线播放音频
  点击文字跳转到对应时间
  自动保存播放进度
```

## 目录结构

```text
courses/                         原始课程视频，长期保存
library/                         Mac 上的长期生成库，不手动改
iphone_export/packages/          传给 iPhone 的 .study 包
ios/StudyPlayer/                 iPhone 原生 App 工程
```

`library/`、`iphone_export/`、`config.toml` 都不会提交到 Git。

## Mac 环境

建议使用 conda 环境：

```bash
conda create -n study_media python=3.11 -y
conda activate study_media
cd /Users/zhaoxin/workspace/study/study_project
python -m pip install --upgrade pip
python -m pip install -e '.[transcribe]'
```

如果还没有 ffmpeg：

```bash
conda install -c conda-forge ffmpeg -y
```

检查环境：

```bash
study-media doctor
```

## 处理并打包一个视频

以 3Blue1Brown 样例为例：

```bash
conda activate study_media
cd /Users/zhaoxin/workspace/study/study_project

study-media process /Users/zhaoxin/workspace/study/courses/3Blue1Brown/Entropy-Compression.mp4
study-media package 3Blue1Brown/Entropy-Compression
```

生成文件：

```text
/Users/zhaoxin/workspace/study/study_project/iphone_export/packages/3Blue1Brown/Entropy-Compression.study
```

`.study` 是单文件学习包，里面包含：

```text
manifest.json
audio.m4a
transcript.json
transcript.md
```

## 安装 iPhone App

详细步骤见：

```text
docs/ios-studyplayer.md
```

工程位置：

```text
ios/StudyPlayer/StudyPlayer.xcodeproj
```

打开 Xcode 后：

```text
选择 StudyPlayer target
Signing & Capabilities
Team 选择你的 Apple Account
连接 iPhone
点击 Run
```

## iPhone 使用

1. AirDrop `Entropy-Compression.study` 到 iPhone。
2. 保存到 `On My iPhone/StudyMedia/Inbox/`，或者直接选择用 `StudyPlayer` 打开。
3. 打开 `StudyPlayer`。
4. 点右上角导入按钮。
5. 选择 `.study` 文件。
6. 进入课程，播放音频，点击文字跳转。

导入成功后，`.study` 已经复制进 App 沙盒；Files 里的原始 `.study` 可以删除。

## 开发验证

Python 测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
PYTHONPATH=src python3 -m compileall -q src tests
```

iOS 无签名构建验证：

```bash
/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild \
  -project ios/StudyPlayer/StudyPlayer.xcodeproj \
  -scheme StudyPlayer \
  -destination generic/platform=iOS \
  CODE_SIGNING_ALLOWED=NO \
  build
```

