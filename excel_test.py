import pandas as pd 
df = pd.DataFrame()
data = [
    ['loo', 1, 2],
    [3, 34, 234.1],
    ['foo', 'doo', 1.1],
    ]


df = pd.DataFrame()

# Creating two columns 
df['A'] = list(map(lambda x: x[0], data))
df['B'] = list(map(lambda x: x[1], data))
df['C'] = list(map(lambda x: x[2], data))
  
# Converting to excel 
df.to_excel('export.xlsx', index = False) 