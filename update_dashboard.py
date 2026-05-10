name: Auto-Update Market Dashboard

on:
  schedule:
    - cron: '0 */2 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GH_PAT }}

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run Analyst Script
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: python update_dashboard.py

    - name: Commit and Push Changes
      run: |
        git config --global user.name "GitHub Action Bot"
        git config --global user.email "actions@github.com"
        git add index.html
        # If there are no changes, exit cleanly with success (exit code 0)
        git diff-index --quiet HEAD || git commit -m "Automated update: Live market dashboard"
        git push
