import pandas as pd
import segregation

df = pd.read_csv("bots.csv")
df = df[df["iteration"] % 20 == 0]
df.to_csv("bots_test.csv")

segregation.clean_data("bots.csv")

df = pd.read_csv("bots_clean.csv")
print(df['iteration'])
