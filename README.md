# 🧠 Ground News Crew – AI Text Analysis Pipeline

This project defines a modular CrewAI workflow that analyzes textual data for bias and other insights. It uses dynamic agents, task configs, 
and Keboola data integration to enable reusable, flexible AI pipelines.

## ⚙️ Environment Variables

Create a `.env` file in the project root and set the following values:

```env
# Keboola Storage API credentials
KBC_API_TOKEN=your_keboola_token
KBC_API_URL=https://connection.keboola.com

# OpenAI credentials
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=o3  # default model (can be, gpt-4o, etc.)
```

## 📥 Input Parameters

The script accepts the following CLI argument:

| Parameter      | Type   | Description                           | Required |
| -------------- | ------ | ------------------------------------- | -------- |
| `--article_id` | string | ID of the article to analyze for bias | ✅ Yes    |

```bash
python run.py --article_id=abc123
```

## 🧪 What It Does

1. Downloads article data from `Keboola` using the provided `article_id`
2. Runs sequential AI tasks to:
   - Extract and analyze textual content.
   - Detect potential bias in tone or framing.
3. Returns a final formatted summary of findings.

## 🧰 Project Structure

```
.
├── run.py                      # Entrypoint CLI script
├── trust_and_bias_analysis/
│   ├── crew.py                 # Crew, agent, and task definitions
│   └── tools/                  # Future: tool wrappers (e.g. download tool)
├── config/
│   ├── agents.yaml             # Agent roles, goals, backstories
│   └── tasks.yaml              # Task descriptions and expected outputs
├── requirements.txt
└── .env                        # Your environment config (not committed)
```

## 🚀 Running Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env  # then edit it to add real credentials

# 3. Run the analysis
python run.py --article_id=your-article-id
```

## ✅ Output

If successful, you’ll see a structured printout like:

```markdown
## Analysis Report
--------------------
Final Results:
Bias Detected: Yes
Explanation: The article exhibits negative framing of one political group without evidence.
```