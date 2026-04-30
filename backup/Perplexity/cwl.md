# Claude's Weekly Limit (CWL)

When I prompt `CWL [weekday] [time] [no.]%` (might shuffle order), apply this prompt for the provided data which is my usage limit with Claude AI. Q: quota usage; T: time elapsed in weekly session.

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
  - brief comment starting with:
    - If Q=T (Q-T=0), pose caution w/ `⚠️`
    - If Q<T (Q-T=negative), reassure w/ `✅`
    - If Q>T (Q-T=positive), alert w/ `🚨`
  - diff quantification:
    - If Q-T ≥ 1 day (~14.3% of week): 🚨 Q is **over-consumed** for [X.X] (1 decimal place) day(s) ahead of T, suggest to resume on [week_day] (when Q=T) if possible
    - If T-Q ≥ 1 day: ✅ Q is **under-consumed** for [X.X] day(s) behind T
  - nothing else