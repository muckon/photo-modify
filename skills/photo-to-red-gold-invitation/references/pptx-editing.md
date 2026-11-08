# 保持原稿的 PPT 原位编辑

## 工具选择

优先使用当前宿主的演示文稿能力，并遵守其导入、验证和交付要求。对于包含大幅高清 PNG、特殊矢量轮廓或用户字体的 PPT，先检查导入前后的渲染。若工具报告图片构造预算超限，或导入会改变原稿，可以对 PPTX 包做有范围的 OOXML 修改，并用原生 PowerPoint 验证；不得用降低原片分辨率来绕过限制后声称高清保留。

附带 `scripts/pptx_materials.py` 使用 Python 3 与 `lxml`；不依赖 `python-pptx`。它可以读取原稿结构，并对显式目标应用 PNG 材质与金色文字，同时保留原摄影资源。通过当前宿主的工作区依赖工具定位运行时，不复制另一台电脑的绝对路径。

## 识别对象

```text
python scripts/pptx_materials.py inspect /private-task/source.pptx
```

输出按真实页面顺序列出页码、对象 ID、类型、边框和文字段落数量，默认不输出文字、对象名称或素材路径。结合渲染预览和用户内容确定纸面与喜字。对象 ID 只在当前源稿内有效，不从示例猜测。

## 应用材质

将下面的匿名配置保存到私人任务目录；所有 `path` 相对配置文件解析。示例 ID 只是示意，必须替换为检查所得值。没有需要改色的文本时，省略 `text`。

```json
{
  "paper": {
    "path": "materials/red-paper.png",
    "targets": [{"slide": 1, "shape_id": "12"}]
  },
  "gold": {
    "path": "materials/gold-paint.png",
    "targets": [{"slide": 1, "shape_id": "24"}]
  },
  "text": {
    "color": "E9CC8B",
    "targets": [{"slide": 1, "shape_id": "36"}]
  },
  "disable_picture_compression": true
}
```

```text
python scripts/pptx_materials.py apply /private-task/source.pptx --config /private-task/materials.json --output /private-task/new-version.pptx --report /private-task/check.json
```

脚本不覆盖既有文件，拒绝不存在或类型不符的对象，给材质分配独立图片关系；不会替换一个可能同时被照片与背景共用的原素材。金漆作为原矢量形状的原生图片填充，按形状比例裁取材质；矢量路径、位置、文字和照片均保留。未点名页面保持原 XML。脚本不会自动把所有文字改成金色。

每次修改后报告源文件及成品摘要、目标对象和变动包条目，不保存实际文字或个人路径。脚本的检查涵盖原资源、文字内容和几何；它不证明视觉效果，需要继续渲染检查。

## 原生 PowerPoint 渲染

Windows 已安装 PowerPoint 时，可在私人任务目录执行：

```text
powershell -File scripts/render_powerpoint.ps1 -DeckPath /private-task/new-version.pptx -OutputDir /private-task/previews -Width 1200 -Height 2000
```

脚本以只读副本打开，导出每页 PNG，不保存或关闭用户已有演示文稿。输出目录必须新建且不在技能目录中。按原页面比例给定宽高；它们不是通用的强制尺寸。

## 视觉与结构验收

对照源稿逐页看纸面是否有接缝、金粉是否过粗、字形是否完整、小字是否清楚，以及背景变化是否暴露原先的浅色底边。文字仍应是文本框，喜字仍应是带图片填充的原矢量形状。

源照片、插画及花朵等未请求改变的资源应字节一致，所有页面的文字内容、字体和位置应保留。若用户另行要求摄影光色改变，则单独验证该改动，不能沿用“照片字节未变”的结论。

按照宿主演示文稿技能完成包完整性与版面检查。只有真正打开检查过 PowerPoint 时才说已在 PowerPoint 检查。最后另存新版本，避免把验证日志、匿名配置以外的实际用户数据或成品带回技能包。
