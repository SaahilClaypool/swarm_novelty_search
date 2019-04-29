import pandas as pd

df = pd.read_csv("../Results/simple_search_fitness2.csv")
df = df.rename(columns = lambda x : x.strip())

best = df[df["segregation"] == df["segregation"].max()]

print(best)
