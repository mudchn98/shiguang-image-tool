# 拾光 Shiguang

轻量级本地图片查看与编辑工具：浏览、拼图、压缩、标注、批处理，内置 AI 抠图与证件照换背景。

A lightweight offline image viewer & editor: browse, collage, compress, annotate, batch tools, local AI cutout and ID-photo background swap.

## 功能

- 浏览：图片查看、缩略图墙、子文件夹浏览（双击进入 / 返回上级）、右键菜单跳转
- 拼图：多图拼接，多种布局（含 L 形、缺角布局），间距/圆角/画质可调
- 压缩：JPEG/PNG 批量压缩、限制最大尺寸
- 编辑：裁剪、旋转、翻转、亮度/对比度/饱和度/锐度、文字/图片水印、AI 抠图、
  证件照一键换背景（白 / 标准蓝 / 红底互转，支持自定义颜色），
  标注工具（打码 / 矩形框 / 箭头 / 直线 / 画圈），复制到剪贴板
- 批处理：批量压缩、改尺寸、转格式、证件照

## 界面

- Glassmorphism 2.0 设计规范
- 深色/浅色双主题，一键切换
- 无边框圆角窗口，自定义标题栏
- 玻璃面板 + 渐变光晕背景

## 技术

Python + PySide6 (Qt) + Pillow + ONNX Runtime
AI 主体分割模型：BiRefNet-Portrait（本地运行，无需联网），
RMBG-1.4 作为模型缺失时的兜底；AI 去背景与证件照换背景共用同一分割模型。

## 目录结构

```
拾光5.2.exe          主程序（免安装，双击即用）
_internal/           运行库与模型（_internal/models/birefnet、_internal/models/rmbg）
README.md            本文件
WHATSNEW.md          版本更新日志
```

首次运行会在 exe 同目录生成 `.shiguang_ver` 版本标记文件，用于判断是否弹出更新说明。

## 版权

本项目采用 [MIT License](LICENSE) 开源协议：可自由使用、复制、修改、分发，只需保留版权声明。

反馈：shiguang.app@qq.com
