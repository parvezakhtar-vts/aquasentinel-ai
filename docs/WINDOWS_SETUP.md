# Windows setup — step by step 🪟

You do **not** need to install Python or anything yourself. Two files do it all.

## Do this ONCE (the night before the demo)

> ⏱️ Takes about 5–15 minutes. You need **internet** for this step.

1. Open the **aquasentinel** folder.
2. Find the file called **`setup.bat`**.
3. **Double-click it.** A black window opens and starts working.
   - If Windows shows a blue “Windows protected your PC” box, click
     **More info → Run anyway** (it’s safe — it’s your own project file).
4. Wait. It will install Python and the tools by itself. Do not close the window.
5. When it says **“Setup complete!”**, you’re done. You can close the window.

That’s it — you never have to do this again on that computer.

## Do this ON DEMO DAY

1. Double-click **`start.bat`**.
2. A black window opens, and after a few seconds your **web browser opens
   automatically** with the dashboard.
3. Leave the black window open the whole time you present.
4. When you’re finished, close the black window to stop it.

## If something goes wrong 😌

- **The browser didn’t open?** Look in the black window for a line like
  `Local URL: http://localhost:8501` and type that into your browser.
- **`start.bat` says “run setup first”?** You skipped step 1 — double-click
  `setup.bat` once, then try `start.bat` again.
- **The pretty version won’t start at the table?** Double-click
  **`start-terminal.bat`** instead. It shows the same results as plain text and
  almost never fails — a perfect backup.
- **`setup.bat` couldn’t install Python?** Install it by hand once:
  go to <https://www.python.org/downloads/>, download Python 3.12, run it, and
  on the **first screen tick “Add python.exe to PATH.”** Then double-click
  `setup.bat` again.

## What these files are (for the curious)

| File | What it does |
| --- | --- |
| `setup.bat` | One-time: installs Python + the packages, prepares demo samples |
| `start.bat` | Opens the pretty dashboard in your browser |
| `start-terminal.bat` | Backup: shows results as plain text, no browser needed |
