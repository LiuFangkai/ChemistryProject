import pandas as pd
data_xls = pd.read_excel('C:/Users/LFK/Desktop/PP LWM/升温曲线.xlsx', 'Sheet1', index_col=None)
data_xls.to_csv('C:/Users/LFK/Desktop/PP LWM/升温曲线.csv', encoding='utf-8')