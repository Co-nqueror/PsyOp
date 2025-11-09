import SQL_Handler

data  = SQL_Handler.data_selection("Students", "Gender")
m = 0
f = 0

for dat in data:
    if 'M' in dat:
        m += 1
    elif 'F' in dat:
        f +=1

print("The number of males in the dataset is " + str(m))
print("The number of females in the data set is " + str(f))