import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd

diff = pd.read_csv(dotabet.train_diff_path)

diff = diff.drop(['match_time', 'match_id', 'radiant_win'], axis=1)
df=diff.groupby('data_win').mean()

fig, ax = plt.subplots(figsize=(14, 7))

# Plot each row
for idx, row in df.iterrows():
    ax.plot(df.columns, row, label=f'data_win={idx}', marker='o')

# Set plot title and labels
ax.set_title('Data Comparison')
ax.set_xlabel('Metrics')
ax.set_ylabel('Values')
ax.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=90)

# Show grid
plt.grid(True)

# Show the plot
plt.tight_layout()
plt.show()