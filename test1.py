import pandas as pd

url = "https://api.data.gov.my/data-catalogue?id=population_malaysia&limit=3" 


df = pd.read_parquet(url)
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

print(df)

import matplotlib.pyplot as plt

x=df['date']
y=df['population']

plt.plot(x,y)
plt.show()