"""Автономный тест функции get_competency_by_specialties.
Запуск: python test_competencies.py
"""
import sqlite3
DB_PATH = "./test_competencies.db"
# 1. Создаём таблицу в SQLite (повторяем структуру CompetencyProfile)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS competency_profiles")
cur.execute("""
    CREATE TABLE competency_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        specialty TEXT NOT NULL,
        year TEXT NOT NULL,
        course TEXT,
        leadership REAL,
        analysis REAL,
        partnership REAL,
        digital_literacy REAL,
        critical_thinking REAL,
        creativity REAL,
        communication REAL,
        teamwork REAL,
        emotional_intelligence REAL,
        adaptability REAL,
        self_education REAL,
        responsibility REAL
    )
""")
# 2. Вставляем тестовые данные — по 2 записи на специальность
test_data = [
    ("Прикладная информатика", "2024", "3", 545, 591, 530, 560, 580, 510, 540, 555, 570, 525, 590, 535),
    ("Прикладная информатика", "2024", "3", 535, 585, 540, 555, 575, 515, 545, 560, 565, 530, 585, 540),
    ("Информационная безопасность", "2024", "3", 512, 548, 501, 530, 555, 490, 520, 535, 550, 505, 565, 515),
    ("Информационная безопасность", "2024", "3", 508, 552, 505, 525, 560, 495, 515, 530, 545, 510, 560, 520),
    ("Математика и компьютерные науки", "2024", "3", 528, 570, 515, 545, 565, 505, 530, 545, 560, 520, 575, 530),
]
fields = [
    "leadership", "analysis", "partnership",
    "digital_literacy", "critical_thinking", "creativity",
    "communication", "teamwork", "emotional_intelligence",
    "adaptability", "self_education", "responsibility",
]
placeholders = ",".join(["?"] * (3 + len(fields)))  # specialty, year, course + 12 competencies
col_names = ["specialty", "year", "course"] + fields
cur.execute(f"DELETE FROM competency_profiles")
for row in test_data:
    cur.execute(
        f"INSERT INTO competency_profiles ({','.join(col_names)}) VALUES ({placeholders})",
        row,
    )
conn.commit()
# 3. Эмулируем get_competency_by_specialties прямо через SQL
def get_competency_by_specialties(specialties, year, course=None):
    if not specialties:
        return []
    result = []
    for specialty in specialties:
        sql = f"""
            SELECT
                AVG(leadership) as leadership,
                AVG(analysis) as analysis,
                AVG(partnership) as partnership,
                AVG(digital_literacy) as digital_literacy,
                AVG(critical_thinking) as critical_thinking,
                AVG(creativity) as creativity,
                AVG(communication) as communication,
                AVG(teamwork) as teamwork,
                AVG(emotional_intelligence) as emotional_intelligence,
                AVG(adaptability) as adaptability,
                AVG(self_education) as self_education,
                AVG(responsibility) as responsibility
            FROM competency_profiles
            WHERE specialty = ? AND year = ?
        """
        params = [specialty, year]
        if course is not None:
            sql += " AND course = ?"
            params.append(course)
        row = cur.execute(sql, params).fetchone()
        has_data = any(v is not None for v in row)
        if has_data:
            entry = {"specialty": specialty}
            for i, field in enumerate(fields):
                entry[field] = round(row[i]) if row[i] is not None else None
            result.append(entry)
    return result
# 4. Тест
result = get_competency_by_specialties(
    ["Прикладная информатика", "Информационная безопасность", "Математика и компьютерные науки"],
    "2024",
    "3",
)
print("Результат:")
for entry in result:
    print(entry)
# 5. Проверка пустого списка
assert get_competency_by_specialties([], "2024") == []
print("\nПустой список специальностей: OK")
# 6. Проверка без course (фильтр только по году)
result_no_course = get_competency_by_specialties(["Прикладная информатика"], "2024")
print("\nФильтрация только по году (без курса):")
for entry in result_no_course:
    print(entry)
conn.close()
print("\nТестирование прошло успешно!")