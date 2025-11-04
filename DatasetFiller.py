import sqlite3
import csv

conn = sqlite3.connect('Dataset.db')
cursor = conn.cursor()


with open('StressLevelDataset.csv', 'r', newline ='') as csvfile:
    i = 0
    reader = csv.reader(csvfile)
    next(reader)

    for line in reader:
        v1 = line[12]
        v2 = line[13]
        v3 = line[14]
        v4 = line[15]
        cursor.execute("INSERT INTO Academic (academic_performance, study_load, teacher_student_relationship, future_career_concerns) VALUES (?, ?, ?, ?);", (v1, v2, v3, v4))
        i += 1
        if i > 842: break

conn.commit()
conn.close()



