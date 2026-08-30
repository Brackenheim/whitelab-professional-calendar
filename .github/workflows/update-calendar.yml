name: Update Professional Calendar

on:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch:

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  update-calendar:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install requests icalendar recurring-ical-events

      - name: Generate filtered calendar
        env:
          OUTLOOK_ICS_URL: ${{ secrets.OUTLOOK_ICS_URL }}
        run: |
          python filter_calendar.py

      - name: Commit calendar
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add public/professional.ics
          git diff --cached --quiet || git commit -m "Update professional calendar"
          git push

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
