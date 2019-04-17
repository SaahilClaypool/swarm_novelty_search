import pandas as pd

df = pd.read_csv("./temp.csv")
print(df)

m = df['segregation'].min()
smallest_seg = df[df['segregation'] == m]
print(smallest_seg)

m = df['segregation'].max()
largest_seg = df[df['segregation'] == m]
print(largest_seg)

