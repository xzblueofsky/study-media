# 使用指南

## 日常流程

处理单个视频：

```bash
study-media process /Users/zhaoxin/workspace/study/courses/3Blue1Brown/Entropy-Compression.mp4
```

生成 iPhone 原生 App 使用的 `.study` 学习包：

```bash
study-media package 3Blue1Brown/Entropy-Compression
```

输出：

```text
/Users/zhaoxin/workspace/study/study_project/iphone_export/packages/3Blue1Brown/Entropy-Compression.study
```

推荐 iPhone Files 临时目录：

```text
On My iPhone/
  StudyMedia/
    Inbox/
      Entropy-Compression.study
```

导入到 `StudyPlayer` 后，Files 里的 `.study` 可以删除。

## 旧 HTML 方案

HTML 仍然可以生成，用于 Mac 上快速预览：

```bash
study-media process /path/to/video.mp4 --embed-audio
```

但 iPhone Files/Quick Look 对 HTML JavaScript 交互支持不稳定，所以正式离线学习推荐使用 `StudyPlayer` App 和 `.study` 包。

## 模型选择

常用选择：

```bash
study-media process video.mp4 --model base
study-media process video.mp4 --model small
study-media process video.mp4 --model medium
```

`base` 更快，`small` 是默认平衡，`medium` 更慢但通常更准。

## 语言选择

英文视频：

```bash
study-media process video.mp4 --language en
```

自动识别：

```bash
study-media process video.mp4 --language auto
```
