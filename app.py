import streamlit as st

1. 基础配置
st.title("AP Course Selection System")
st.write("请填写信息并选课。每一组必须至少选一门。")

2. 个人信息
st.header("Step 1: Information")
cn_name = st.text_input("中文名")
en_name = st.text_input("英文名")
grade = st.selectbox("年级", ["G9", "G10", "G11", "G12"])
class_name = st.text_input("班级")
country = st.text_input("申请国家")
major = st.text_input("专业方向")

3. 课程数据
humanities = []
h_list = ['World History', 'American History', 'Psychology', 'Business study', 'Micro Economics', 'Macro Economics']
for item in h_list:
humanities.append("Pre-AP " + item)
humanities.append("AP " + item)

course_groups = {
"Group 1 (Chinese)": ["中文"],
"Group 2 (English)": ["ESL", "AP English 10", "AP English language and composition", "AP English Literature"],
"Group 3 (Humanities)": humanities,
"Group 4 (Science)": ["Pre-AP Physics", "AP Physics 1", "AP Physics 2", "AP Physics C Mechanics", "AP Physics C E&M", "Pre-AP Chemistry", "AP Chemistry", "Pre-AP Biology", "AP Biology"],
"Group 5 (Math)": ["AP pre-Calculus", "AP Calculus AB", "AP Calculus BC", "AP Statistics", "AP Computer Science A", "AP Seminar"],
"Group 6 (Arts)": ["AP 2D art and design", "AP 3D art and design"]
}

4. 渲染选课
st.header("Step 2: Select Courses")
selections = {}

for g_name, courses in course_groups.items():
st.write("---")
st.subheader(g_name)
selected_in_group = []
for c in courses:
if st.checkbox(c, key=g_name+c):
selected_in_group.append(c)
selections[g_name] = selected_in_group

5. 逻辑校验 (Physics C vs Pre-Calculus)
conflict = False
has_pre_calc = "AP pre-Calculus" in selections["Group 5 (Math)"]
selected_science = selections["Group 4 (Science)"]
physics_c = [s for s in selected_science if "Physics C" in s]

if has_pre_calc and len(physics_c) > 0:
conflict = True
st.error("错误：选择了 AP pre-Calculus 就不能选 Physics C 系列。")
st.warning("提示：Physics C 需要先修或同修 Calculus。")

6. 提交
if st.button("提交选课"):
missing_group = [g for g, s in selections.items() if len(s) == 0]
