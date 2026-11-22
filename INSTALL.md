# Installing Abejandr0's GitHub profile 🐝

1. On GitHub, create a new **public** repository named **Abejandr0** (same as your username). Initialize it with a README if you want. Its URL will be `https://github.com/Abejandr0/Abejandr0`.
2. Upload **README.md**, **scripts/generate_bee.py**, **.github/workflows/bee.yml**, and **assets/bee-contributions.svg** from this archive, **preserving their paths**. The included SVG is explicitly marked as an illustrative demo, not your real contributions yet.
   - Easiest from Linux: clone the newly created repo, copy the files into it, commit and push.
3. Open repository **Actions → 🐝 Update honey bee contributions → Run workflow**. This runs the generator with the repo's built-in `GITHUB_TOKEN` and replaces the demo calendar with your **real GitHub contribution data**. It will run daily thereafter.
4. If you get a push permission error, open **Settings → Actions → General → Workflow permissions** and enable **Read and write permissions** for `GITHUB_TOKEN` (if your repository's settings allow it). Alternatively adjust repository policy. The workflow itself requests `contents: write`.
5. Confirm `assets/bee-contributions.svg` no longer shows "DEMO DATA" at the bottom. Your profile will now show the animated real calendar.

The source and animation are SVG; nothing is sent to any third-party service besides GitHub's API. Public profile data only. Do not commit your personal access tokens. The workflow uses the built-in short-lived GitHub token. Because GitHub Actions' scheduled jobs may occasionally be delayed, the update time is approximate.

If you want to test the appearance offline:

```bash
python scripts/generate_bee.py --demo
```

**Important:** `--demo` generates illustrative activity **only** and should never be used to represent real GitHub activity; run the Action afterward.
