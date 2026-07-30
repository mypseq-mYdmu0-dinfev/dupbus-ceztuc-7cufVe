# TEMP File —— Mail Handover for CCSIM07

⚠️ **`temp_` FILE** —— exists solely to carry `~/Library/Mail` context across the session boundary. Delete once the discussion concludes.

## 1. Purpose and Source
- 1.1. Substance below reproduces §89 of `ccsim_response_202607291831.md` and §100–103 of `ccsim_response_202607291950.md` in full, plus the owner's follow-up in `ccsim_query_202607291950.md`.
- 1.2. Goal: CCSIM07 can keep answering follow-ups on those four sections without re-running any investigation.
- 1.3. Cross-referenced against `ccsim_close_202607291954.md` §5.1–5.2 —— that close log confirms the issue is still open and nothing has been actioned.

## 2. Measured Breakdown of `~/Library/Mail`
- 2.1. Two independent audits, run in separate turns, agree within normal drift (small gap = live changes between measurements, not error).
- 2.2. Audit 1 (§89.2–89.3): whole folder 7.0GB; cached attachments 3.63GB; cached `.emlx` message bodies 2.94GB; Envelope Index 336MB.
- 2.3. Audit 2 (§101.2, later): attachments 3.59GB across 709 folders; `.emlx` bodies 2.94GB; Envelope Index 333MB; whole folder 6.9GB.
- 2.4. Both audits verified the four figures cross-check internally (attachments + bodies + index ≈ whole folder), so the split is trustworthy, not estimated.
- 2.5. Structure verified (not assumed): `Attachments/` and `Messages/` are sibling folders at every level; ZERO `.emlx` files exist inside any `Attachments/` folder. Deleting attachments cannot touch a message body.
- 2.6. Separately: the System-Settings "Mail" size row bundles OTHER paths too (notably a 5.3GB Spotlight index living outside this folder) —— that is why an earlier casual estimate ran higher than the measured 7.0GB/6.9GB.

## 3. Accounts —— Why Type Matters
- 3.1. 7 accounts total, ALL verified IMAP or Exchange, NO POP.
- 3.2. Matters because IMAP/Exchange are server-authoritative —— the server holds the real copy, so the local cache (attachments + bodies) is safe to delete; it just re-downloads on demand.
- 3.3. A POP account would be local-only (deleting the cache would be the ONLY copy) —— not applicable here, since none of the 7 are POP.
- 3.4. The real local-only risk sits OUTSIDE these 7 accounts entirely —— see §4.

## 4. "On My Mac" Store —— Original Finding + Owner's Update
- 4.1. ORIGINAL FINDING (§89.4, first audit): one store, ID `D3622DCB`, is "On My Mac" —— 153 messages that exist on NO server anywhere.
- 4.2. Breakdown of those 153: 147 Outbox messages spanning 2023–2026; 1 crash-recovered message; 4 SCHEDULED Send-Later messages that would be silently cancelled if deleted.
- 4.3. This was the single data-loss risk in the whole exercise —— everything else in §2 is disposable cache backed by a server.
- 4.4. OWNER'S UPDATE (`ccsim_query_202607291950.md` §89.4, verbatim): "i don't use 'On My Mac'; i also just cleared the 'On My Mac' label and 'All Drafts' in 'Mail' so it should be emptied now."
- 4.5. ⚠️ This is the OWNER'S REPORT ONLY —— nothing has re-verified the store is actually empty after his clearing action. No follow-up audit ran.
- 4.6. Prior CC reply (§96.2) treated it as resolved ("With 'On My Mac' emptied, the folder is now pure cache") but that is inference from his report, not a re-measurement.
- 4.7. If CCSIM07 or the owner want certainty, the store would need re-auditing before any deletion that assumes it is empty.

## 5. Attachments-Only Deletion —— Exact Commands (verbatim from §101.3–101.4)
- 5.1. DRY RUN first —— prints every folder and a grand total, changes nothing:
```bash
find "/Users/culous/Library/Mail" -type d -name "Attachments" -print0 | xargs -0 du -sh 2>/dev/null
find "/Users/culous/Library/Mail" -type d -name "Attachments" -print0 | xargs -0 du -ck 2>/dev/null | tail -1 | awk '{printf "TOTAL: %.2f GB\n", $1/1024/1024}'
```
- 5.2. THEN the delete —— empties each `Attachments/` folder, leaves bodies and the index untouched:
```bash
find "/Users/culous/Library/Mail" -type d -name "Attachments" -print0 | xargs -0 -I{} find {} -mindepth 1 -delete
```
- 5.3. After running: message text renders instantly (read straight from the `.emlx`); an attachment re-downloads on demand the first time it is opened; nothing needs rebuilding, so search stays fast.
- 5.4. Some attachments are stored INLINE in the `.emlx` itself and are unaffected either way.

## 6. Quitting Mail Fully —— Not Achievable, and Why It Does Not Matter Here
- 6.1. Correction to an earlier suggestion (§101.6): fully quitting Mail so nothing holds the index does NOT work.
- 6.2. `maild` (the always-on sync daemon) and the Spotlight extension hold the Envelope Index open even with the window closed; macOS restarts them regardless.
- 6.3. Irrelevant to §5's deletion —— that delete never touches the index, only the `Attachments/` folders.
- 6.4. Only real precaution: avoid running the delete mid-sync.

## 7. Download Attachments: `Recent` —— Full Reconciliation
- 7.1. Owner's screenshot (`Screenshot 2026-07-29 at 19.41.02.png`, §89.8/102.1) confirms `Recent` is set, and per his reply it is the same on all 7 accounts.
- 7.2. Earlier "no value stored" observation was ALSO correct —— macOS only persists a preference key when a NON-default value is chosen; `Recent` IS the shipped default, so choosing it writes nothing to disk. Both observations are true at once; neither side was wrong.
- 7.3. The mechanism that actually matters: `Recent` is a FORWARD-ONLY download gate (Apple's own definition: attachments received within the past 15 months) —— it is NOT a retention or eviction policy.
- 7.4. Nothing ever evicts an attachment already downloaded, no matter how old it later becomes.
- 7.5. Hence 2018-era attachments persisted: they were fetched when they were recent at the time, or the message was opened once since.
- 7.6. ⚠️ Consequence: the §5 cleanup is NOT one-off —— expect to repeat it every 6–12 months unless the setting is changed to `None` per account (pure on-demand fetch, nothing pre-cached).

## 8. Time Machine —— Two Corrections and the Inverted Plan
- 8.1. Current state: `/Users/culous/Library` sits in Time Machine's exclusion list, set by the owner years ago, reason forgotten (his guess: assumed it was all disposable system data).
- 8.2. CORRECTION 1 (§103.1): actual size is 69GB, measured live with `du`, NOT the ~444GB the owner remembered (`ccsim_query_202607291950.md` §89.5). The size argument for excluding it is far weaker than either side assumed.
- 8.3. CORRECTION 2 (§103.2): VERIFIED —— a subfolder of an excluded parent CANNOT be re-included. Time Machine's exclusion is a pure ancestor check with no override, confirmed both by direct test on the machine and the man page. So "carve out just Mail" is impossible in principle, not just impractical.
- 8.4. Genuinely irreplaceable items found inside the excluded `~/Library`, currently backed up NOWHERE:
  - 8.4.1. `Messages/` —— 50MB (SMS history, syncs to no other device/service).
  - 8.4.2. `Keychains/login.keychain-db` —— 43MB.
  - 8.4.3. Signal's local message store —— 1.04GB (Signal has no cloud backup by design).
  - 8.4.4. Notes group container —— 159MB.
  - 8.4.5. A Photos library —— 236MB, sitting unusually inside `~/Library`.
- 8.5. Recommended, inverted plan (§103.4): REMOVE the blanket `~/Library` exclusion entirely, then exclude only the actual churn: `Caches` (3.4GB), `Metadata` (5.3GB), `HTTPStorages`, `Biome`, `DuetExpertCenter`, `IntelligencePlatform`.
- 8.6. Easiest path given in source: System Settings ▸ General ▸ Time Machine ▸ Options —— it handles the privilege elevation automatically.
- 8.7. Source notes a CLI (`tmutil`) equivalent exists but needs `sudo`; the exact CLI syntax was NOT spelled out in the original response, so it is not reproduced here to avoid fabricating a command —— use the GUI path above, or ask CCSIM07 to derive the exact `tmutil` invocation fresh if the CLI route is wanted.
- 8.8. Net effect of the inverted plan (§103.5): everything irreplaceable in §8.4 gets backed up for the first time, whilst ~9GB of pure churn stays excluded —— overall backup size and churn barely move.

## 9. Incidental Find —— Stuck Messages Cache
- 9.1. 7.4GB of stuck cache found at `~/Library/Containers/com.apple.MobileSMS/Data/tmp/TemporaryItems` (§103.6).
- 9.2. Not message data —— just litter. Independent of every decision above; worth a look regardless of what the owner decides on Mail or Time Machine.

## 10. For CCSIM07 —— What To Do With This File
- 10.1. On resuming this discussion, remind the owner he can re-read §89 (`ccsim_response_202607291831.md`) and §100–103 (`ccsim_response_202607291950.md`) himself —— he does not need to retype his points; he can reply by number (e.g. "re 89.4:", "re 103.4:") as normal.
- 10.2. Three open decisions await the owner, none defaulted or assumed:
  - 10.2.1. Whether to run the §5 attachment-only deletion (dry-run then delete).
  - 10.2.2. Whether to change the Time Machine exclusion per the §8.5 inverted plan.
  - 10.2.3. Whether to switch Download Attachments from `Recent` to `None` on all 7 accounts.
- 10.3. ⚠️ STATE PLAINLY, do not let this drift: NOTHING in §2–9 has been actioned. Every deletion and every setting change described here is the owner's to perform himself, not something CC or an SA has already done.
- 10.4. Once the owner resolves all three decisions in §10.2 and confirms he is done with the topic, this `temp_` file should be deleted (Void Rule —— rename to `❌_temp_mail_context_202607301941.md` and let the owner delete it manually; never delete it directly).
