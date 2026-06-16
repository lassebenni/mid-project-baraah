# AI Assistance Log

Document every time you used an AI tool during this project: what you asked, what it gave you, and what you changed before using it.

This is not about proving you worked hard. It is about building the habit of treating AI output as a first draft, not a final answer.

## Tools used

<!-- List the AI tools you used, e.g. Claude, GitHub Copilot, ChatGPT -->
Claude 
-

## Log

<!-- One entry per significant AI interaction. Add as many as you need. -->

### Entry 1

**What I asked:** <!-- Paste or summarise the prompt -->
my pipeline runs successfully and inserts rows into Postgres, but the log never shows 'Uploaded raw data to blob' - the raw JSON isn't appearing in Azure Blob Storage. What's going wrong?"
**What it gave me:** <!-- Summarise the output -->
After reviewing part of pipeline.py, pointed out that save_raw() was defined twice in the file. The first definition called upload_raw_json(raw_data) (uploads to Azure Blob Storage), but a second definition later in the same file wrote the data to a local raw.json file instead and in Python, the second definition silently overrides the first. So run() was actually calling the local file version and the Blob upload was never executed.
Recommended removing the second (incorrect) definition and keeping only the one that calls upload_raw_json().
**What I changed:** <!-- What you added, removed, or corrected before using it -->
i found both definitions of save_raw(), deleted the one
that wrote to raw.json and rerun the pipeline. Confirmed the log now showed INFO Uploaded raw data to blob: pipeline/2026-06-14_202115.json, and verified the file actually existed by checking the raw container in the Azure Portal.
---
