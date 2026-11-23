# 电子游戏风 Video Game（现代引擎 / 3A CG）

> 现代游戏引擎画面质感：实时渲染感、HUD 界面、游戏化镜头。区别于像素艺术（复古 2D），这里指 3A/虚幻引擎的 3D 质感。游戏过场/实况/CG 向高频。

> ⚠️ 与 `pixel-art.md` 分工：像素=复古低分辨率 2D；本包=现代 3D 引擎渲染。用户说"游戏感"先判是哪种。

## ① 一句话基调
**引擎渲染 + 游戏镜头 + 可选 HUD。** 画面像"正在玩的 3A 游戏"——高精度 3D、特定游戏视角、可带界面元素。

## ② 光线配置
| 项 | 写法 |
|---|---|
| 质感 | 实时全局光照 GI、屏幕空间反射、体积光、动态阴影——"引擎感" |
| 标志 | 虚幻引擎式电影级光照、HDR 高光、光线追踪反射 |
| 禁忌 | 平涂无光影（那是别的风格） |

## ③ 色彩调性
| 项 | 用法 |
|---|---|
| 主色 | 按游戏类型：写实军事（去饱和冷硬）、奇幻（高饱和瑰丽）、生存（阴郁） |
| 质感 | 高动态范围、后期泛光 bloom、色彩分级明显 |

## ④ 镜头与构图
| 项 | 配置 |
|---|---|
| 视角 | **这是重点**——第三人称越肩(TPS)、第一人称(FPS，长段易眩晕慎用)、俯视 ARPG、过场电影镜 |
| 构图 | 游戏化：主角居偏侧留操作空间、过场用电影构图 |
| HUD | 可选叠加血条/小地图/准星/任务提示（要"游戏感"就加，要"CG 电影感"就去掉） |
| 运镜 | 第三人称跟随、锁定环绕、过场动态运镜 |

典型元素：虚幻引擎质感、角色模型、场景关卡、HUD 界面、技能特效、过场 QTE。

## ⑤ 质感与禁忌
必备：3D 引擎渲染质感、明确游戏视角、GI/反射/体积光、可选 HUD、后期 bloom。
禁忌：❌ 像素低分辨率（那是 pixel-art）❌ 手绘平涂 ❌ 真实纪录片质感。

## 提示词模板
```
[主体/场景] rendered in Unreal Engine 5, AAA game cinematic, 
third-person over-shoulder view, real-time global illumination, 
volumetric lighting, screen-space reflections, HDR bloom, 
[可选：game HUD with minimap and health bar], 
high-detail 3D models, cinematic game cutscene quality
```
关键词组合拳：Unreal Engine + AAA game + 视角(TPS/过场) + global illumination + volumetric + HDR bloom + 可选 HUD。
