# Implementation and tooling log

- Source acquisition attempt 1: directory API succeeded; downloading its Unicode `download_url` raised `UnicodeEncodeError`. Ordinary URL encoding bug, fixed by percent-encoding the URL before urllib request. No scientific outputs existed; not a Skill gap.
