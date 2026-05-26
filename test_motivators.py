"""Автономный тест функции get_motivator_profile_by_specialties.
Запуск: python test_motivators.py
"""
import sqlite3
DB_PATH = "./test_motivators.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS motivator_profiles")
cur.execute("""
    CREATE TABLE motivator_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        specialty TEXT NOT NULL,
        year TEXT NOT NULL,
        course TEXT,
        career REAL, altruism REAL, creativity REAL,
        money REAL, power REAL, independence REAL,
        knowledge REAL, communication REAL, recognition REAL,
        safety REAL, achievement REAL, self_development REAL,
        leadership REAL, teamwork REAL, stability REAL, challenge REAL
    )
""")
motivator_fields = [
    "career", "altruism", "creativity",
    "money", "power", "independence",
    "knowledge", "communication", "recognition",
    "safety", "achievement", "self_development",
    "leadership", "teamwork", "stability", "challenge",
]
# 2 записи на специальность
rows = [
    # Прикладная информатика — больше карьера/деньги
    ("Прикладная информатика", "2024", "3",
     620, 480, 590, 600, 550, 580, 610, 520, 540, 500, 570, 590, 560, 530, 510, 550),
    ("Прикладная информатика", "2024", "3",
     610, 490, 580, 590, 540, 570, 600, 530, 550, 510, 560, 580, 555, 535, 515, 545),
    # Психология — больше альтруизм/общение
    ("Психология", "2024", "3",
     510, 650, 530, 480, 450, 520, 590, 640, 580, 560, 540, 620, 510, 600, 550, 520),
    ("Психология", "2024", "3",
     520, 640, 540, 490, 460, 530, 600, 650, 590, 570, 550, 630, 520, 610, 560, 530),
]
col_names = ["specialty", "year", "course"] + motivator_fields
placeholders = ",".join(["?"] * len(col_names))
for row in rows:
    cur.execute(
        f"INSERT INTO motivator_profiles ({','.join(col_names)}) VALUES ({placeholders})",
        row,
    )
conn.commit()
def get_motivator_profile_by_specialties(specialties, year, course=None):
    if not specialties:
        return []
    result = []
    for specialty in specialties:
        avg_cols = ",".join(f"AVG({f}) as {f}" for f in motivator_fields)
        sql = f"SELECT {avg_cols} FROM motivator_profiles WHERE specialty = ? AND year = ?"
        params = [specialty, year]
        if course is not None:
            sql += " AND course = ?"
            params.append(course)
        row = cur.execute(sql, params).fetchone()
        has_data = any(v is not None for v in row)
        if has_data:
            entry = {"specialty": specialty}
            for i, field in enumerate(motivator_fields):
                entry[field] = round(row[i]) if row[i] is not None else None
            result.append(entry)
    return result
# Тест 1: обе специальности
result = get_motivator_profile_by_specialties(
    ["Прикладная информатика", "Психология"],
    "2024", "3",
)
print("Тест 1: со специальностями")
for entry in result:
    print(entry)
# Проверка средних
assert result[0]["specialty"] == "Прикладная информатика"
assert result[0]["career"] == 615, f"Expected 615, got {result[0]['career']}"
assert result[0]["altruism"] == 485, f"Expected 485, got {result[0]['altruism']}"
assert result[1]["specialty"] == "Психология"
assert result[1]["altruism"] == 645, f"Expected 645, got {result[1]['altruism']}"
assert result[1]["career"] == 515, f"Expected 515, got {result[1]['career']}"
print("OK — average values match\n")
# Тест 2: пустой список
assert get_motivator_profile_by_specialties([], "2024") == []
print("Тест 2: пустой список специальностей")
print("OK\n")
# Тест 3: без курса (выборка по году)
result3 = get_motivator_profile_by_specialties(["Прикладная информатика"], "2024")
print("Тест 3: без фильтрации курса")
print(result3[0] if result3 else "empty")
print("OK\n")
# Тест 4: несуществующая специальность → пусто
result4 = get_motivator_profile_by_specialties(["Нет такой"], "2024")
print("Тест 4: несуществующая специальность")
print(result4 if result4 else "[] — correctly excluded")
assert result4 == []
print("OK\n")
conn.close()
print("Тестирование прошло успешно!")