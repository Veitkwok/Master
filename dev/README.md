# dev（不上 Bot）

本地开发/校验工具。安装到 Bot 的只有 `skills/finance-master/`。

| 文件 | 用途 |
|------|------|
| `check_pack.py` | 结构/路径/禁词/大小/方法核 hash 检查。`--write-hash` 更新方法核 hash；`--installed PATH` 检查已安装副本 |
| `validate_card.py` | 校验一张建议卡 JSON 是否满足决策红线 |
| `tests/test_cards.py` | 建议卡金样/反例（12 例） |
| `samples/` | 数据包 / job / 建议卡样例（可跑 validate_card） |
| `research/deepseek-integration.md` | DeepSeek 接入方案与实测清单 |
| `publish-to-github.sh` | 从 monorepo 发布本包到 GitHub 分发仓库 |
| `vendor/normalize_engine.py` | 引擎迁移归一脚本（路径/工具名/边界补丁，可重跑） |
| `hash-manifest.json` | 方法核 SHA256（check_pack 校验） |

常用命令：

```bash
python3 dev/check_pack.py
python3 dev/tests/test_cards.py
python3 dev/validate_card.py dev/samples/advice-card.sample.json
python3 skills/finance-master/scripts/deepseek_analyze.py --selftest
```
