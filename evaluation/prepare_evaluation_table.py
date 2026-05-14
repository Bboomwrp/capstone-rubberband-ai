import pandas as pd

# =====================================================
# TEMPLATE
# =====================================================

rows = [

    {
        "Metric": "Close Match Ratio (%)",
        "Baseline": "",
        "RL": "",
        "Improvement": ""
    },

    {
        "Metric": "Snowball Ratio (%)",
        "Baseline": "",
        "RL": "",
        "Improvement": ""
    },

    {
        "Metric": "Comeback Rate (%)",
        "Baseline": "",
        "RL": "",
        "Improvement": ""
    },

    {
        "Metric": "Average End HP Diff",
        "Baseline": "",
        "RL": "",
        "Improvement": ""
    },

    {
        "Metric": "Median End HP Diff",
        "Baseline": "",
        "RL": "",
        "Improvement": ""
    },

    {
        "Metric": "Round Duration (sec)",
        "Baseline": "",
        "RL": "",
        "Improvement": ""
    },

    {
        "Metric": "Close Match Increase",
        "Baseline": "",
        "RL": "",
        "Improvement": ""
    },

    {
        "Metric": "Snowball Reduction",
        "Baseline": "",
        "RL": "",
        "Improvement": ""
    }
]

df = pd.DataFrame(rows)

print(df)

df.to_csv(
    "evaluation_table_template.csv",
    index=False
)

print()
print("✅ TEMPLATE SAVED")
