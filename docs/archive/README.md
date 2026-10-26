# Historical Documentation Archive

The five reports below were moved with `git mv` from the repository root. This
archive is recorded on 2026-10-26 against migration baseline `5c4a52290de8e59527048e931f2334b06009c2c7`. Their file contents are preserved byte-for-byte;
this index is the only path mapping added by the move. Historical reports retain the
literal names they used when written, including references to other historical files.

| Original path | Archived path | Report date | Phase / stage | Original observed / source Git boundary | Committed report boundary | Scope |
| --- | --- | --- | --- | --- | --- | --- |
| `FINAL-RC-DECISION.md` | [`release-readiness/FINAL-RC-DECISION.md`](release-readiness/FINAL-RC-DECISION.md) | 2026-08-06 | Phase 12 final RC preparation | `aacbde449a6dbc8723d5c866033ac195017a90e5` | commit `d1d6170b640724b9d41c97a7619088771f54390c`; tree `baca42a59414d3c577928202ef064096253e67ff` | Historical RC readiness decision and release-gate classification. |
| `RC-READINESS-REPORT.md` | [`release-readiness/RC-READINESS-REPORT.md`](release-readiness/RC-READINESS-REPORT.md) | 2026-08-06 | Phase 11-B Host Acceptance and RC readiness | `aacbde449a6dbc8723d5c866033ac195017a90e5` | commit `d1d6170b640724b9d41c97a7619088771f54390c`; tree `baca42a59414d3c577928202ef064096253e67ff` | Historical release-readiness audit and Host Acceptance boundary. |
| `DISTRIBUTION-003-REPORT.md` | [`distribution/DISTRIBUTION-003-REPORT.md`](distribution/DISTRIBUTION-003-REPORT.md) | 2026-08-07 | Distribution-003 | `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66` plus the four Distribution-002.1 corrections disclosed in the report | commit `b482c9c990b9912d99230460bcd7540b64fd74fa`; tree `3401dd0ca81c766581349f7491e55c501f0b859c` | Historical Bash distribution probe and packaging boundary. |
| `DISTRIBUTION-ACCEPTANCE-REPORT.md` | [`distribution/DISTRIBUTION-ACCEPTANCE-REPORT.md`](distribution/DISTRIBUTION-ACCEPTANCE-REPORT.md) | 2026-08-07 | Distribution-002 / 002.1 acceptance | `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66`, with the disclosed uncommitted Distribution-002.1 overlay for its correction checks | commit `b482c9c990b9912d99230460bcd7540b64fd74fa`; tree `3401dd0ca81c766581349f7491e55c501f0b859c` | Historical packaging acceptance and D002-F01 correction. |
| `DISTRIBUTION-BASH-VALIDATION.md` | [`distribution/DISTRIBUTION-BASH-VALIDATION.md`](distribution/DISTRIBUTION-BASH-VALIDATION.md) | 2026-08-07 | Distribution-003-A | `a4c83f8b3ce90f6e388cf32b398a4d01667f9b66` plus the four disclosed Distribution-002.1 corrections | commit `096f804b906ed735205555e6e336fc97ef7a282f`; tree `b78260099eb7032da41b168e315a7a3c4232a354` | Historical Git Bash lifecycle and payload-integrity validation. |

The observed/source column identifies what each report actually tested; the
committed-report column locates the preserved report before this move. Neither
column predicts later results or converts an uncommitted overlay into a tested
commit. They are historical evidence boundaries, not the current `main` boundary and not release
authority. Phase 14/15 records, evaluation history, raw logs, and review artifacts
remain at their existing paths and are not reclassified by this archive.
Referenced Task boundaries remain valid for their original scope.

## Content Integrity

The migration compared each archived file's raw bytes with its original Git blob
at `5c4a522`. Every pair is identical; root copies are absent. These blob IDs are
content checks for the move, not behavioral evidence or release authorization.

| Original filename | Original and archived Git blob |
| --- | --- |
| `FINAL-RC-DECISION.md` | `9844e6a17b704089122dba4d08d390f52aa6118c` |
| `RC-READINESS-REPORT.md` | `338d9bc87cd4b734973634a9b5dfbab7ca2b6203` |
| `DISTRIBUTION-003-REPORT.md` | `02bfd14eb9cd25ad8e570433121cd4f224c5ce28` |
| `DISTRIBUTION-ACCEPTANCE-REPORT.md` | `9eb8b060cee9701d6b92753fdab1ebd867e3907a` |
| `DISTRIBUTION-BASH-VALIDATION.md` | `c35976d99a124721f4e9af2f0859d71c3a301e2d` |

## Content integrity

The migration compares each baseline Git blob with the archived file's raw bytes.
Both paths below identify the same blob; no root duplicate is retained.

| Report | Baseline and archived Git blob |
| --- | --- |
| `FINAL-RC-DECISION.md` | `9844e6a17b704089122dba4d08d390f52aa6118c` |
| `RC-READINESS-REPORT.md` | `338d9bc87cd4b734973634a9b5dfbab7ca2b6203` |
| `DISTRIBUTION-003-REPORT.md` | `02bfd14eb9cd25ad8e570433121cd4f224c5ce28` |
| `DISTRIBUTION-ACCEPTANCE-REPORT.md` | `9eb8b060cee9701d6b92753fdab1ebd867e3907a` |
| `DISTRIBUTION-BASH-VALIDATION.md` | `c35976d99a124721f4e9af2f0859d71c3a301e2d` |
