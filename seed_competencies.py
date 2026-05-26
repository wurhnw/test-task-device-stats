"""Наполнение competency_profiles тестовыми данными для PostgreSQL.

Запуск (после docker compose up -d):
    python seed_competencies.py
"""
import os
import sys

os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_USER"] = "stats"
os.environ["POSTGRES_PASSWORD"] = "stats"
os.environ["POSTGRES_DB"] = "stats"

from app.db.session import SessionLocal
from app.models.models import CompetencyProfile

db = SessionLocal()

db.query(CompetencyProfile).delete()

fields = [
    "leadership", "analysis", "partnership",
    "digital_literacy", "critical_thinking", "creativity",
    "communication", "teamwork", "emotional_intelligence",
    "adaptability", "self_education", "responsibility",
]

rows = [
    ("Прикладная информатика", "2024", "3", 545, 591, 530, 560, 580, 510, 540, 555, 570, 525, 590, 535),
    ("Прикладная информатика", "2024", "3", 535, 585, 540, 555, 575, 515, 545, 560, 565, 530, 585, 540),
    ("Прикладная информатика", "2024", "4", 550, 595, 535, 565, 585, 520, 545, 560, 575, 530, 595, 540),
    ("Информационная безопасность", "2024", "3", 512, 548, 501, 530, 555, 490, 520, 535, 550, 505, 565, 515),
    ("Информационная безопасность", "2024", "3", 508, 552, 505, 525, 560, 495, 515, 530, 545, 510, 560, 520),
    ("Математика и компьютерные науки", "2024", "3", 528, 570, 515, 545, 565, 505, 530, 545, 560, 520, 575, 530),
]

for row in rows:
    specialty, year, course = row[0], row[1], row[2]
    values = row[3:]
    cp = CompetencyProfile(
        specialty=specialty,
        year=year,
        course=course,
        **dict(zip(fields, values)),
    )
    db.add(cp)

db.commit()
count = db.query(CompetencyProfile).count()
db.close()

print(f"Inserted {count} rows into competency_profiles (PostgreSQL).")
print("\nTest the endpoint:")
print("http://localhost:8000/competencies/by-specialties?specialties=Прикладная+информатика,Информационная+безопасность&year=2024&course=3")
