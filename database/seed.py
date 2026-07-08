from datetime import date, timedelta
from random import choice, randint, sample, uniform

from faker import Faker

from database.database import get_session
from database.models import (
    Application,
    ApplicationSource,
    ApplicationStatus,
    Candidate,
    Gender,
    Job,
    Skill,
)

fake = Faker()



JOBS = [
    ("Software Engineer", "Engineering"),
    ("Backend Engineer", "Engineering"),
    ("Frontend Engineer", "Engineering"),
    ("AI Engineer", "AI"),
    ("Machine Learning Engineer", "AI"),
    ("Data Scientist", "Data"),
    ("Data Analyst", "Data"),
    ("DevOps Engineer", "Infrastructure"),
    ("QA Engineer", "Engineering"),
    ("Product Manager", "Product"),
]

LOCATIONS = [
    "Cairo",
    "Giza",
    "Alexandria",
    "Mansoura",
    "Assiut",
]

SKILLS = [
    "Python",
    "SQL",
    "Docker",
    "Git",
    "Linux",
    "FastAPI",
    "Flask",
    "Django",
    "TensorFlow",
    "PyTorch",
    "Machine Learning",
    "Deep Learning",
    "Power BI",
    "Tableau",
    "AWS",
    "Azure",
    "Kubernetes",
    "JavaScript",
    "React",
    "Pandas",
]



def create_jobs(session):

    jobs = []

    for title, department in JOBS:

        job = Job(
            title=title,
            department=department,
            location=choice(LOCATIONS),
        )

        session.add(job)
        jobs.append(job)

    session.commit()

    return jobs



def create_skills(session):

    skills = []

    for skill_name in SKILLS:

        skill = Skill(name=skill_name)

        session.add(skill)
        skills.append(skill)

    session.commit()

    return skills



def create_candidates(session, skills):

    candidates = []

    for _ in range(500):

        candidate = Candidate(

            full_name=fake.name(),

            age=randint(21, 45),

            gender=choice(
                [
                    Gender.MALE,
                    Gender.FEMALE,
                ]
            ),

            city=choice(LOCATIONS),

            experience_years=round(
                uniform(0, 15),
                1,
            ),
        )

        candidate.skills = sample(
            skills,
            randint(3, 7),
        )

        session.add(candidate)

        candidates.append(candidate)

    session.commit()

    return candidates




def create_applications(
    session,
    candidates,
    jobs,
):

    for candidate in candidates:

        number_of_applications = randint(1, 3)

        selected_jobs = sample(
            jobs,
            number_of_applications,
        )

        for job in selected_jobs:

            application = Application(

                candidate=candidate,

                job=job,

                status=choice(
                    list(ApplicationStatus)
                ),

                source=choice(
                    list(ApplicationSource)
                ),

                salary_expectation=randint(
                    8000,
                    50000,
                ),

                created_at=date.today()
                - timedelta(
                    days=randint(
                        0,
                        365,
                    )
                ),
            )

            session.add(application)

    session.commit()



def seed_database():

    session = get_session()

    print("Creating Jobs...")
    jobs = create_jobs(session)

    print("Creating Skills...")
    skills = create_skills(session)

    print("Creating Candidates...")
    candidates = create_candidates(
        session,
        skills,
    )

    print("Creating Applications...")
    create_applications(
        session,
        candidates,
        jobs,
    )

    session.close()

    print("Database seeded successfully.")


if __name__ == "__main__":
    seed_database()