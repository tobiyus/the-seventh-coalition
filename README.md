# The Seventh Coalition: Road to 60

A pixel-art leaderboard for the guild's climb to level 60 on WoW Forever (EU, Normal).

- `index.html` is the whole page. The roster lives in the `guild-data` block inside it.
- `refresh.py` reads the public guild roster page on armorywowforever.com and rewrites that block.
- `.github/workflows/refresh.yml` runs the refresh every hour and commits the result.

The pixel characters are original drawings generated from each member's race and class.
Not affiliated with Blizzard Entertainment.
