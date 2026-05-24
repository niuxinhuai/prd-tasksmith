# Implementation Task Table

| ID | Task | Owner | Risks |
|---:|------|-------|-------|
| 1 | 距离过期 7 天内展示提醒条 | frontend / app | 时区、秒/毫秒单位和边界时间容易出错 |
| 2 | 未登录用户不展示 | frontend / app | 登录态和权限分支需要覆盖 |
| 3 | 点击提醒条跳转到续费页 | frontend / app | 路由路径和参数需要联调确认 |
| 4 | 接口返回 expireTime 字段，单位为秒 | backend / service | 接口失败、字段缺失和兼容旧数据需要兜底<br>时区、秒/毫秒单位和边界时间容易出错 |

