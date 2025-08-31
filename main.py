import streamlit as st
import pandas as pd
import tempfile
import shutil
st.write("# Alpha Progression Visualizer")
csv = st.file_uploader("Upload CSV-file", accept_multiple_files=False, type=["csv"])

def findMaxWeight(l:list)-> float:
    max = 0
    filteredList = [row for row in l if "KG" not in row]
    for index, set in enumerate(filteredList):
        if index == 0:
            continue
        weight = float(set.split(";")[1].replace(",", "."))
        if weight > max:
            max = weight

    return max
#tests
def calculateOneRepMax(weight:float, reps:int)->float:
    return weight * (1 + 0.0333 * reps)

def findBiggestOneRepMax(l: list)-> float:
    maxOneRepMax = 0
    oneRepMax = 0
    filteredList = [row for row in l if "KG" not in row]
    for index, set in enumerate(filteredList):
        if index == 0:
            continue
        weight = float(set.split(";")[1].replace(",", "."))
        reps = int(set.split(";")[2])
        oneRepMax = calculateOneRepMax(weight, reps)
        if oneRepMax > maxOneRepMax:
            maxOneRepMax = oneRepMax

    return round(maxOneRepMax,2)

def generateOneRepMaxCourse(l:list)->dict:
    oneRepMaxList = []
    oneRepMaxCourse =  {"sets": [], "1RMs": []}
    listWithoutHeader = [row for row in l if "KG" not in row]

    for index, set in enumerate(listWithoutHeader):
        weight = float(set.split(";")[1].replace(",", "."))
        reps = int(set.split(";")[2])
        oneRepMaxList.append(calculateOneRepMax(weight, reps))

    for j in range(len(oneRepMaxList)-2):
        oneRepMaxCourse["sets"].append(f"Set {j}")
    oneRepMaxCourse["1RMs"] = oneRepMaxList[::-1]
    oneRepMaxCourse["1RMs"] = oneRepMaxCourse["1RMs"][0:-2]

    return oneRepMaxCourse

def findMostCommonExercise(data:csv)->dict:
    mostSets = {"exerciseName": "", "sets":0}

    for key in data.keys():
        if len(data[key]) > mostSets["sets"]:
            mostSets["sets"] = len(data[key])
            mostSets["exerciseName"] = key

    return mostSets

def extractTrainingdata(csv)->dict:
    daten = dict()
    if csv is not None:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(csv, tmp)
            tmp_path = tmp.name

    with open(tmp_path, "r", encoding="utf-8-sig") as f:
        lines = [line.strip() for line in f]
        lines = [line.replace("\"", "") for line in lines if line != ""]  

    for index, line in enumerate(lines):
        exercise = ""
        exerciseRange = int()

        if line[1] == ".":
            exerciseList = " ".join(line.split("·")[0:2])
            exercise = exerciseList[2::]
            for i in range(index + 1, len(lines)):
                if (lines[i][1] == "."):
                    exerciseRange = i

                    break
            for j in range(index + 2, exerciseRange):
                if "-" not in lines[j]:
                    if exercise in daten.keys():
                        daten[exercise].append(lines[j])
                    else:
                        daten[exercise] = ["Set;KG;reps"] + [lines[j]]

    for key in daten.keys():
        daten[key] = [entry for entry in daten[key] if len(entry) < 13 and not entry.isalpha() and len(entry.split(";")) == 3]

    return daten

if "training_data" not in st.session_state:
    st.session_state.training_data = None


if st.button("Exercise statistics") and csv:
    st.session_state.training_data = extractTrainingdata(csv)
    st.write("### Most common exercise")
    st.write(f"{findMostCommonExercise(st.session_state.training_data)["exerciseName"]}\n sets: {findMostCommonExercise(st.session_state.training_data)["sets"]}")


if st.session_state.training_data:
    choice = st.selectbox("Select an exercise: ", options=st.session_state.training_data.keys())
    sets = len(st.session_state.training_data[choice])
    maxWeight = findMaxWeight(st.session_state.training_data[choice])
    oneRepMax = findBiggestOneRepMax(st.session_state.training_data[choice])
    tenRepMax = round(oneRepMax *0.75, 2)
    stats = {"Amount of sets (alltime)":[sets], "Biggest used weight":[maxWeight], "1RM (alltime)": [oneRepMax], "10RM (alltime)":[tenRepMax] }
    statsDf = pd.DataFrame(stats)
    st.table(statsDf)
    if st.button("show 1RM course"):
        oneRepMaxCourse = pd.DataFrame(generateOneRepMaxCourse(st.session_state.training_data[choice]))
        oneRepMaxCourse["set_num"] = range(1, len(oneRepMaxCourse) + 1)  
        df_course = oneRepMaxCourse.set_index("set_num")
        st.line_chart(oneRepMaxCourse["1RMs"])










