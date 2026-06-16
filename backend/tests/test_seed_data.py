from app.db.init_data import init_demo_data
from app.models import Course, Exercise, KnowledgePoint, KnowledgeSource, User


def test_seed_creates_demo_users(db_session):
    init_demo_data(db_session)
    users = db_session.query(User).all()
    usernames = [u.username for u in users]
    assert "demo_student" in usernames
    assert "demo_teacher" in usernames


def test_seed_creates_course_with_enough_data(db_session):
    init_demo_data(db_session)
    courses = db_session.query(Course).all()
    assert len(courses) == 1
    assert courses[0].name == "操作系统"

    kp_count = db_session.query(KnowledgePoint).count()
    assert kp_count >= 40, f"Need >=40 knowledge points, got {kp_count}"

    ex_count = db_session.query(Exercise).count()
    assert ex_count >= 60, f"Need >=60 exercises, got {ex_count}"

    src_count = db_session.query(KnowledgeSource).count()
    assert src_count >= 8, f"Need >=8 sources, got {src_count}"


def test_seed_has_case_materials(db_session):
    init_demo_data(db_session)
    kps_with_cases = db_session.query(KnowledgePoint).filter(KnowledgePoint.case_materials != "").count()
    assert kps_with_cases >= 8, f"Need >=8 KPs with case_materials, got {kps_with_cases}"


def test_seed_is_idempotent(db_session):
    init_demo_data(db_session)
    init_demo_data(db_session)
    assert db_session.query(User).count() == 2
