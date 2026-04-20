# Claude's Weekly Limit (CWL)

When I prompt `CWL [weekday] [time] [no.]%`, apply this prompt for the provided data which is my usage limit with Claude AI.

## Example
e.g. Input = `sun 12pm 10%` means:
- This weekly session starts & ends on Sunday at 12pm (SYD time)
  - e.g. `week_start` = last SUN 12pm
  - e.g. `week_end` = next SUN 12pm
- I already used 10% of weekly quota

## Your Missions
- Extract Q (above example=10)
- Calculate T with current SYD time (`now`)
  - formula: (`now` - `week_start`) ÷ (`week_end` - `week_start`) ×100
- Respond with:
  - amount of: Q, T, and (Q-T)
  - plus:
    - If Q=T, pose caution w/ `⚠️`
    - If Q<T, reassure w/ `✅`
    - If Q>T, alert w/ `🚨`
  - nothing else