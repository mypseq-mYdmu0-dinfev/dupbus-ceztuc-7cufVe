<!-- dlint: deliverable -->

# elint Live Probe

This file is the one-step liveness probe for `cscpt/elint.py`. Edit it with the Edit or Write tool and watch what happens.

- ALIVE: an `[elint]` advisory naming this file appears in context, and a new `post:advise` line is appended to `cscpt/.elint.log`.
- DEAD: the write succeeds in silence and the log does not grow. There is no third outcome.

The `<!-- dlint: deliverable -->` marker on line 1 is LOAD-BEARING, exactly as the word `response_` is load-bearing in `hook_probe_response_.md`. This file sits under `cp/`, which elint treats as Claude Project protocol territory and never flags, so without that marker the probe would prove nothing whilst appearing to be a valid test. Never remove it, and never move this file out of the sandbox to "fix" it.

This paragraph exists so the probe clears elint's substance floor, which drops stubs, placeholders and index fragments before any other rule is consulted. A probe that fell below the floor would be silent for a second reason entirely, and a probe with two independent ways of failing silently is worse than none at all, because a green result would no longer tell you which mechanism was actually exercised.

Do NOT run `dlint.py` on this file. A clean FULL run would write a receipt covering this exact content, and the probe would then go quiet for good, since a receipted file is precisely what elint is built to stop nagging about.
