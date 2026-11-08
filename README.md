# photo-modify

可复用的摄影设计工作流与 Codex 技能。

## 红纸金漆婚礼请柬

[photo-to-red-gold-invitation](skills/photo-to-red-gold-invitation/SKILL.md) 将真实照片制作成实景撕纸拼贴请柬，并支持接续用户自行修改过的 PowerPoint，另存红纸纹理、金漆和金粉版本。

- 保留真实人像，不进行面部或发型重绘。
- 纸面、笔触和摄影分层，文字使用可编辑文本框。
- 原喜字矢量轮廓使用金漆图片填充，保留可编辑形状。
- 按需进行非生成式光色调整，保留源片与已接受版本。
- 附通用 PPT 结构检查、定点材质修改与 Windows PowerPoint 渲染脚本。

### 安装与使用

把 `skills/photo-to-red-gold-invitation` 整个文件夹复制到 Codex 的个人技能目录（通常是 `~/.codex/skills/`），重新打开会话后使用：

```text
用 $photo-to-red-gold-invitation 把我提供的照片做成实景拼贴婚礼请柬，
保留真实人像，文字可编辑，另存红纸金漆版本。
```

已有 PPT 时：

```text
用 $photo-to-red-gold-invitation 接续这个已保存的 PPT，
只给红底增加纸纹、给原喜字增加金漆金粉质感，另存一版。
```

脚本需要 Python 3 与 `lxml`；原生渲染脚本需要 Windows PowerPoint。生成材质使用宿主内置图像工具，不需要单独的第三方服务或 API Key。

### 数据范围与许可

仓库中的技能仅含通用说明、匿名示例和通用代码，不包含用户照片、请柬成品、姓名、婚期、地址、本机路径或聊天记录。运行时素材与输出保存在使用者自己的任务目录。

构图思路参考 Zeejay0 的 Gathered Scenes Zine，本技能为明确标识的改写与扩展。保留作者与个人非商业许可；详见 [来源说明](skills/photo-to-red-gold-invitation/references/sources-and-license.md) 和 [完整许可](skills/photo-to-red-gold-invitation/LICENSE)。
