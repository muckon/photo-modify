# 独立材质提示词

使用宿主内置图像工具生成材质，生成后复制到用户任务目录。以下内容只包含通用材质要求；不要上传人物照片、整张请柬或含个人文字的截图。图片实际生成尺寸以结果为准，不把提示词里的理想尺寸当作输出保证。

## 红色纤维纸

```text
Asset type: flat material texture for a Chinese wedding invitation background.
Generate only a full-frame red handmade art-paper surface, vertical 3:5.
Edge-to-edge red dyed cotton or xuan paper, with fine irregular short fibers,
softly pressed shallow grain, and slight natural tonal mottling. Dominant warm
crimson around #B61D32, or the supplied approved red. Tactile and refined;
visible texture at normal viewing distance, restrained enough for small light
gold text. Flat scanner-like illumination and sparse tiny flecks in nearby red
shades. No white flecks, textile weave, leather, velvet, gold, lettering, symbols,
objects, brushstrokes, folds, heavy crumpling, vignette, borders, watermark or
perspective. A flat material swatch, not an invitation.
```

对照当前接受的红色检查色相。细纹应在完整请柬上仍有感觉，但不要放大到像毛毡或粗皮革。若金字变难读，先降低材质明暗反差，不通过描粗文字改变用户排版。

## 金漆与金粉

```text
Asset type: flat gold lacquer and gold-powder swatch for filling an existing
vector double-happiness glyph. Generate only a full-frame square material.
Warm champagne gold lacquer, satin metallic paint with embedded fine gold
powder and irregular microscopic gold-leaf flecks. Dense subtle metallic grain,
with a few slightly larger bright particles. Gentle broad variation around
#DFBE73; pale champagne highlights around #F5DFA0 and restrained antique-gold
accents around #B88C42. Many tiny irregular reflective particles that remain
perceptible when reduced into a calligraphic symbol. Flat and evenly lit,
edge-to-edge. No symbol, calligraphy, text, red, transparency, objects, watermark,
lens flare, star-shaped sparkles, bokeh, coins, loose-glitter piles, mirror
reflections, folds, heavy black patches or harsh scratches. Material only;
the existing vector outline supplies the glyph.
```

把纹理填进原喜字轮廓，不让模型重新生成喜字。放到整页尺寸检查颗粒，避免做成砂纸、塑料亮片或纯黄色噪点。可保留轻微大面积明暗层次，细颗粒提供金粉感；文字仍可保持原来的清晰浅金色，不强行给小字铺颗粒。

## 生成记录

在私人任务目录记录所用提示词、内置工具模式、最终选用素材路径与实际尺寸。可分享技能只保留这些通用提示词；不打包用户生成记录、素材截图或含姓名的文件名。不要为了复用材质自动接入第三方作者网站、API 或充值服务。
