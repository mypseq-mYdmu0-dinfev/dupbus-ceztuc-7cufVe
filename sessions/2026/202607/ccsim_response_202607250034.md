# Response to ccsim_query_202607250034.md
*OptGuideOnDeviceModel: DELETABLE now (disable the flag so it stays gone)*

## 1. Verdict —— DELETABLE NOW
- 1.1. What it is (SA-confirmed): Chrome's Optimization-Guide ON-DEVICE model —— the local Gemini Nano weights (`weights.bin` = 4.27GB) Chrome's component-updater silently pre-fetches for on-device AI features. `manifest.json` inside names it "Optimization Guide On Device Model / v3Nano". No user/profile data —— just a signed model blob + config + two EMPTY runtime caches.
- 1.2. It's on the INTERNAL SSD —— it sits under `Chrome/` (a real dir), NOT under `Chrome/Default` (which is the symlink to FURY). So deleting it frees ~4.27GB on the 94%-health internal disk directly. That's the good news.
- 1.3. Static + unused: the payload hasn't changed since 5 Feb (5.5⁺ months); the `encoder_cache.bin`/`adapter_cache.bin` are 0 bytes, i.e. the on-device model appears to have NEVER actually been used for inference —— it was proactively downloaded, not earned by use.
- 1.4. Regenerable —— it's managed by Chrome's component-updater, so deleting it ALONE only frees the space TEMPORARILY: Chrome will silently re-download the ~4GB on a future background check unless you disable the feature flag first.

## 2. Safe procedure (I do NOT delete data —— run this yourself)
- 2.1. To make it STICK (prevent the silent re-download): in Chrome, open `chrome://flags`, set `#optimization-guide-on-device-model` to Disabled (and `#prompt-api-for-gemini-nano` to Disabled), click Relaunch.
- 2.2. Then quit Chrome fully (⌘Q; confirm `pgrep -x "Google Chrome"` returns nothing).
- 2.3. Delete:
```bash
rm -rf "/Users/culous/Library/Application Support/Google/Chrome/OptGuideOnDeviceModel"
```
- 2.4. Relaunch Chrome. With the flag off, the ~4GB stays freed. (Skip step 2.1 and it just comes back on a later background update.)
- 2.5. Note —— its tiny siblings in `Chrome/` (`OnDeviceHeadSuggestModel`, `OptGuideOnDeviceClassifierModel`, Widevine, cert-revocation, etc.) are the same component-updater family but negligible in size; leave them.
