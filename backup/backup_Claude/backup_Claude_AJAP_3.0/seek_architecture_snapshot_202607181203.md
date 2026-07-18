# seek/ architecture snapshot (excl. gcl/) —— 202607181203

One-shot, read-only inventory of the retired old-AJAP `seek/` tree, taken immediately BEFORE its Phase 8 move to `backup/backup_Claude/backup_Claude_AJAP_3.0` (migration plan `inv/2026/202607/migration_plan_202607180103.md`). The 4077 `gcl/` ARs (migrated data, merged into `AJAP_repo/gcl/`) are deliberately EXCLUDED; this file records the architecture/doctrine artefacts that justify the retire.

**203 files** still under `seek/` at snapshot time (excl. `gcl/`).

## Already migrated out (no longer under seek/)

The 7 live-context files and the interview notes were moved to `cp/career/` in Phases 4-5 (202607180420s); `config.CONTEXT_DIR` was repointed there in the Phase 5 code sweep. Listed for completeness:

| Former path (under seek/) | Role |
|---|---|
| `context/pro_profile.md` | candidate facts (live-context) —— MOVED → cp/career/ 202607180420s |
| `context/gcl.md` | CL doctrine (live-context) —— MOVED → cp/career/ 202607180420s |
| `context/ccl.md` | consulting-CL doctrine (live-context) —— MOVED → cp/career/ 202607180420s |
| `context/culous_yu_resume_ats.md` | worker/auditor résumé facts (live-context) —— MOVED → cp/career/ 202607180420s |
| `context/culous_yu_portfolio.md` | worker portfolio facts (live-context) —— MOVED → cp/career/ 202607180420s |
| `context/culous_yu_linkedin.md` | worker LinkedIn facts (live-context) —— MOVED → cp/career/ 202607180420s |
| `context/virtual_presentation.md` | presentation URL (live-context) —— MOVED → cp/career/ 202607180420s |
| `interviews/` | real interview notes (career-adjacent) —— MOVED → cp/career/ 202607180420s |

## Still under seek/ at snapshot (bound for backup 3.0)

| Path (under seek/) | Role |
|---|---|
| `.DS_Store` | macOS Finder cruft |
| `.claude/.DS_Store` | macOS Finder cruft |
| `.claude/post_compact.sh` | old PostCompact hook script —— retired, never ported |
| `.claude/settings.json` | old PostCompact hook settings —— retired, never ported |
| `.claude/settings.local.json` | old local Claude settings —— retired, never ported |
| `.claude/tmp/.DS_Store` | macOS Finder cruft |
| `.claude/tmp/Culous_Yu_Resume_Consulting.pdf` | generated résumé PDF (temp junk) —— voided ❌_ at retire |
| `.claude/tmp/Culous_Yu_Resume_IxD.pdf` | generated résumé PDF (temp junk) —— voided ❌_ at retire |
| `.claude/tmp/Culous_Yu_Resume_Marketing.pdf` | generated résumé PDF (temp junk) —— voided ❌_ at retire |
| `.claude/tmp/hb_marker` | old MA/SA heartbeat marker (empty)  —— DISSOLVED |
| `.claude/tmp/hb_reread_marker` | old MA/SA heartbeat marker (empty)  —— DISSOLVED |
| `.claude/tmp/last_decision.md` | old MA last-decision marker —— DISSOLVED |
| `.claude/tmp/ma_c2_marker` | old MA/SA heartbeat marker (empty)  —— DISSOLVED |
| `.claude/tmp/ma_full_reread_marker` | old MA/SA heartbeat marker (empty)  —— DISSOLVED |
| `.claude/tmp/ma_hb_reread_marker` | old MA/SA heartbeat marker (empty)  —— DISSOLVED |
| `.claude/tmp/ma_msg.md` | old MA mailbox (single-use approvals) —— DISSOLVED (state.Ledger approvals) |
| `.claude/tmp/ma_state.md` | old MA state marker —— DISSOLVED (ledger reopen on restart) |
| `.claude/tmp/sa2_alert.md` | old SA2 watchdog alert marker —— DISSOLVED |
| `.claude/❌_ajap_login.local_moved_ajap.md` | voided old login file —— credentials relocated to ~/.ajap 202607071013 |
| `CLAUDE.md` | old seek OTG/session instructions —— legacy, retired |
| `README.md` | old seek readme —— legacy, retired |
| `ccl/ccl_archive/placeholder.md` | empty ccl archive placeholder |
| `ccl/placeholder.md` | empty ccl AR home placeholder (no real ARs) |
| `context/.DS_Store` | macOS Finder cruft |
| `context/MA_hb.md` | old MA heartbeat answer-sheet/markers —— DISSOLVED (ledger recovery replaces heartbeat) |
| `context/SA2_hb.md` | old SA2 bash watchdog —— DISSOLVED (asyncio supervision) |
| `context/ajap.md` | old scoring/flow doctrine —— ABSORBED into core/scoring + config + browser/seek + prompts |
| `context/cl_check.py` | old CL checker —— ported to core/linter.py (factual v2) |
| `context/main_ajap.md` | old MA orchestration —— ABSORBED into orchestrator.py |
| `context/mini_numbered.md` | superseded by protocols/mini_numbered.md |
| `context/mini_replace.md` | DROP —— dead, no consumer (voided ❌_ at retire) |
| `context/mini_writing.md` | superseded by protocols/mini_writing.md + config.GENAI_WORDS |
| `context/psl.md` | superseded by protocols/psl.md |
| `investigation/.DS_Store` | old investigation-session artefact (history) |
| `investigation/2026/.DS_Store` | old investigation-session artefact (history) |
| `investigation/2026/202605/.DS_Store` | old investigation-session artefact (history) |
| `investigation/2026/202605/audit_202605240519.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/audit_202605251920.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/audit_202605252220.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/changes_202605240610.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/changes_202605240639.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/changes_202605250333.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/changes_202605300615.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/changes_202605300913.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/changes_202605310402.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/close_202605230601.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/close_202605240519.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/close_202605250456.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/close_202605300931.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/close_202605310448.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605150400.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605231736.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605232218.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605240401.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605240454.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605242201.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605242243.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605250031.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605251925.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605300604.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605300927.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605302236.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605310340.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/query_202605310448.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605150400.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605231736.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605232218.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605240401.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605240454.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605242201.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605242243.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605250031.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605252351.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605300604.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605300927.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605302236.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605310402.md` | old investigation-session artefact (history) |
| `investigation/2026/202605/response_202605310448.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/.DS_Store` | old investigation-session artefact (history) |
| `investigation/2026/202606/MA_hb_LEAN_PROPOSAL_202606272232.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/audit_202606040352.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/audit_202606060452.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/audit_202606062012.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/audit_202606081836.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/audit_202606271729.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/audit_202606272146.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606050721.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606060503.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606080108.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606091942.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606120333.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606120346.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606121035.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606121128.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606271643.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606271704.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606271833.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606272057.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606272146.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202606272232.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202607042016.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202607042058.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/changes_202607042112.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/close_202606060640.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/close_202607050412.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606040346.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606050715.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606060448.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606060625.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606062031.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606080108.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606091942.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606120333.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606120346.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606120406.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606121035.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606121128.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606262114.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606271632.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606271704.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606271721.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606271829.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606271906.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606271954.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606272023.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606272052.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606272139.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202606272232.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202607042008.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202607042053.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202607042108.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/query_202607050410.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606040346.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606050715.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606060448.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606060625.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606062031.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606091942.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606120333.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606120346.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606120406.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606121035.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606121128.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606262114.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606271632.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606271704.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606271721.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606271829.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606271906.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606271954.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606272023.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606272052.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606272139.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202606272232.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202607042008.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202607042053.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202607042104.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202607042108.md` | old investigation-session artefact (history) |
| `investigation/2026/202606/response_202607050410.md` | old investigation-session artefact (history) |
| `investigation/2026/202607/query_202607050412.md` | old investigation-session artefact (history) |
| `investigation/2026/query_.md` | old investigation-session artefact (history) |
| `investigation/CLAUDE.md` | old investigation-session artefact (history) |
| `investigation/InvSes.md` | old investigation-session artefact (history) |
| `investigation/README.md` | old investigation-session artefact (history) |
| `investigation/query_.md` | old investigation-session artefact (history) |
| `queue.md` | old Qi queue prose —— superseded by core/queue.py + AJAP_repo/queue.md |
| `runtime/.DS_Store` | macOS Finder cruft |
| `runtime/rchat_202605231637_1st_max_long_run.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202605241601_1st_agent.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202605242104.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202605250606.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202605251914.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202605252210.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202605302038.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202606062005.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202606121024.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202606121749.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202606131233.txt` | old CC-session chat transcript (runtime) |
| `runtime/rchat_202606141723.txt` | old CC-session chat transcript (runtime) |
| `runtime/rlog_202605250711.md` | old runtime decision log |
| `runtime/rlog_202605251707.md` | old runtime decision log |
| `runtime/rlog_202605251836.md` | old runtime decision log |
| `runtime/rlog_202605251910.md` | old runtime decision log |
| `runtime/rlog_202605300805.md` | old runtime decision log |
| `runtime/rlog_202605300825.md` | old runtime decision log |
| `runtime/rlog_202605300935.md` | old runtime decision log |
| `runtime/rlog_202605302239.md` | old runtime decision log |
| `runtime/rlog_202605302302.md` | old runtime decision log |
| `runtime/rlog_202605310518.md` | old runtime decision log |
| `runtime/rlog_202605311407.md` | old runtime decision log |
| `runtime/rlog_202606050729.md` | old runtime decision log |
| `runtime/rlog_202606060646.md` | old runtime decision log |
| `runtime/rlog_202606080251.md` | old runtime decision log |
| `runtime/rlog_202606120410.md` | old runtime decision log |
| `runtime/rlog_202606131857.md` | old runtime decision log |
| `runtime/rlog_202606142048.md` | old runtime decision log |
| `runtime/rlog_202606150710.md` | old runtime decision log |
| `runtime/rlog_202606182140.md` | old runtime decision log |
| `runtime/rlog_202606192237.md` | old runtime decision log |
| `runtime/rlog_202606201506.md` | old runtime decision log |
| `runtime/rlog_202606202330.md` | old runtime decision log |
| `runtime/rlog_202606272329.md` | old runtime decision log |
| `runtime/rlog_202607042122.md` | old runtime decision log |
