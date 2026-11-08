# 标准底色、笔触与独立素材

## 配色依据

已有接受版本的素材与颜色优先。新建标准版时，可用下列色彩作为起点，再按原片、纸面和文字可读性调整；不是全局调色滤镜。

| 对象 | 起始方向 | 用法 |
| --- | --- | --- |
| 纸面 | 淡黄米白，示例 `#F5E6CF` | 温暖、低反差，避免鲜黄、明显脏斑或过重纤维 |
| 主笔触 | 蓝色至蓝灰，示例 `#2C5091` | 承担来源轮廓与视线动线，不遮住人物 |
| 辅助笔触 | 暖灰，示例 `#8E8376` | 少量呼应主笔触，避免额外色块竞争 |
| 喜字与强调 | 朱红，示例 `#B61D32` | 保持清楚、平面、克制；复用原字形 |
| 正文 | 深棕，示例 `#5B4736` | 在浅纸面上有足够对比，不自动替换用户确定的字体 |

新稿默认是暖纸平面效果。并不主动增加红色底面、金色小字、金属渐变、金粉或镜面高光；这些属于用户另行指定的风格变体。

## 纸面提示词

仅在缺少可用纸面或用户要求重新制作时生成，已有接受素材直接复用。

```text
Generate only a full-frame pale warm ivory paper surface, vertical 3:5.
Fine handmade art-paper grain and sparse short fibers, diffuse flat scan light,
low-contrast natural variation around a soft warm cream such as #F5E6CF.
Quiet, clean and spacious, suitable behind dark-brown small invitation text.
Edge-to-edge flat paper, no text, symbols, illustrations, people, objects,
strong stains, folds, heavy crumpling, fabric weave, red field, metallic gold,
glitter, vignette, frame, watermark, perspective or cast shadows.
```

检查实际输出尺寸和色相，不把提示词里的方向或色值当成生成保证。纹理在正常尺寸只需轻微可感，不能与摄影和排版争夺注意。

## 场景衍生笔触提示词

先从源片提取主导轮廓，再把方括号内容换成匿名场景描述；不向生成式工具提交人物照片或含个人文字的整页。

```text
Create only an isolated abstract blue-and-warm-grey printmaking accent on a
genuinely transparent background. Use [one dominant contour from the scene]
to form one broad directional brush passage and a small supporting grey trace.
Dry pigment, restrained paper-print texture, broad quiet masses and open gaps.
Flat and orthographic. Reserve [the planned quiet area] as empty space.
No people, faces, hair, photography, lettering, wedding information, icons,
repeated decorative motifs, metallic effects, 3D depth, shadows or mockup.
```

按内置图像工具的透明背景选项请求真实 Alpha，并在合成前检查。保留一到两个主导动作，不能通过不断添加细碎纹理凑出“拼贴感”。

## 纸面与摄影交界

边缘遮罩由版面几何与已接受构图确定，而不是让模型重画人物。主要交界应不规则、带窄纤维和少量露纸；减少均匀白边、光晕、粗糙颗粒和独立漂浮小块。背景、装饰和摄影分层检查，不对整幅图使用按肤色或婚纱颜色筛选的替换。
