import sqlite3
import csv

conn = sqlite3.connect('Dataset.db')
cursor = conn.cursor()

working_table = "Physiological"

# For Students
with open('Stress_Dataset.csv', 'r', newline='') as csvfile:
    if working_table == "Students":
        i = 0
        reader = csv.reader(csvfile)
        next(reader)
        
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = \'Academic\';")
        cursor.execute("DELETE FROM Academic;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = \'Psychological\'")
        cursor.execute("DELETE FROM Psychological")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = \'Physiological\'")
        cursor.execute("DELETE FROM Physiological")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = \'Students\'")
        cursor.execute("DELETE FROM Students")
        for line in reader:
            v1 = line[1]
            v2 = line[0]
            if int(v1) < 18 or int(v1) > 22: continue
            if int(v2) == 0: v2 = "M"
            elif int(v2) == 1: v2 = "F"
            cursor.execute("INSERT INTO Students (age, gender) VALUES (?, ?)", (v1, v2))

        
# For others
with open('StressLevelDataset.csv', 'r', newline ='') as csvfile:
    i = 0
    reader = csv.reader(csvfile)
    next(reader)

    if working_table == "Academic":
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = \'Academic\';")
        cursor.execute("DELETE FROM Academic;")
        for line in reader:
            v1 = line[12]
            v2 = line[13]
            v3 = line[14]
            v4 = line[15]
            cursor.execute("INSERT INTO Academic (academic_performance, study_load, teacher_student_relationship, future_career_concerns) VALUES (?, ?, ?, ?);", (v1, v2, v3, v4))
            i += 1
            if i == 777: break
        
    if working_table == "Psychological":
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = \'Psychological\'")
        cursor.execute("DELETE FROM Psychological")
        for line in reader:
            v1 = line[0]
            v2 = line[1]
            v3 = line[2]
            v4 = line[3]
            cursor.execute("INSERT INTO Psychological (anxiety_level, self_esteem, mental_health_history, depression) VALUES (?, ?, ?, ?);", (v1, v2, v3, v4))
            i += 1
            if i == 777: break

    if working_table == "Physiological":
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = \'Physiological\'")
        cursor.execute("DELETE FROM Physiological")
        for line in reader:
            v1 = line[5]
            v2 = line[7]
            v3 = line[6]
            v4 = line[4]
            cursor.execute("INSERT INTO Physiological (blood_pressure, breathing_problem, sleep_quality, headache) VALUES (?, ?, ?, ?);", (v1, v2, v3, v4))
            i += 1
            if i == 777: break

conn.commit()
conn.close()



