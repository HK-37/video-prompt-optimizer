# 像素艺术 Pixel Art

> 复古游戏美学：低分辨率点阵、有限色板、硬边无抗锯齿。怀旧/8bit/16bit 游戏感，MV 和游戏向视频高频。

## ① 一句话基调
**点阵 + 有限色板 + 硬边。** 一切都由可见的方块像素构成，颜色少而明确，没有渐变柔化。

## ② 光线配置
| 项 | 写法 |
|---|---|
| 质感 | 光影用色块台阶表现（dithering 抖动），非连续渐变 |
| 标志 | 高光/阴影是成块的色阶跳变，不是平滑过渡 |
| 禁忌 | 真实柔光、体积光、光晕（像素世界没有这些连续光效） |

## ③ 色彩调性
| 项 | 用法 |
|---|---|
| 主色 | 有限调色板（16/32 色感），高饱和、色块分明 |
| 风格分支 | 8bit（更粗更少色）/ 16bit（更细更多色，如 SNES 质感） |
| 禁忌色 | 连续渐变、真实感肤色、低饱和写实 |

## ④ 镜头与构图
| 项 | 配置 |
|---|---|
| 视角 | 2D 横版 side-scroller / 俯视 top-down / 2.5D 斜 45°等距 isometric |
| 构图 | 居中或网格对齐，元素对齐像素格 |
| 运镜 | 整屏平移/卷轴式移动（像游戏画面滚动），避免真实镜头运动 |

典型元素：方块地形、像素角色精灵 sprite、点阵 UI/血条、马赛克粒子特效。

## ⑤ 质感与禁忌
必备：可见像素点阵、硬边、抖动渐变 dithering、有限色板、扫描线（可选 CRT 复古）。
禁忌：❌ 抗锯齿柔边 ❌ 真实光影 ❌ 3D 透视畸变 ❌ 写实材质。

## 提示词模板
```
[主体/场景] in retro pixel art style, 16-bit SNES aesthetic, 
limited color palette, hard-edged pixels, no anti-aliasing, 
dithered shading, side-scroller composition, 
sprite-based characters, flat bold colors, 
optional CRT scanlines, nostalgic game look
```
关键词组合拳：pixel art + 16-bit + limited palette + hard-edged + dithering + no anti-aliasing + sprite。
8bit 变体：`16-bit SNES` 换 `8-bit NES, chunkier pixels, fewer colors`。
