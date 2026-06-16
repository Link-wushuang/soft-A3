from sqlalchemy import inspect

from app.models import (
    AgentTask,
    AgentTrace,
    AnswerRecord,
    Course,
    Exercise,
    GeneratedResource,
    KnowledgePoint,
    KnowledgeSource,
    LearningPath,
    LearningPathNode,
    ProfileUpdateLog,
    SafetyAuditLog,
    StudentProfile,
    User,
)


def test_all_tables_created(db_session):
    tables = inspect(db_session.bind).get_table_names()
    expected = [
        "user",
        "course",
        "knowledge_point",
        "knowledge_source",
        "student_profile",
        "profile_update_log",
        "learning_path",
        "learning_path_node",
        "agent_task",
        "agent_trace",
        "generated_resource",
        "exercise",
        "answer_record",
        "safety_audit_log",
    ]
    for table in expected:
        assert table in tables, f"Missing table: {table}"


def test_create_user(db_session):
    user = User(username="demo_student", password_hash="hashed", role="student")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.role == "student"


def test_create_course_with_knowledge_point(db_session):
    course = Course(name="操作系统", description="OS course")
    db_session.add(course)
    db_session.commit()
    kp = KnowledgePoint(
        course_id=course.id,
        chapter="文件系统",
        title="索引分配",
        summary="索引块保存数据块地址",
        difficulty="medium",
        tags=["file-system", "indexed-allocation"],
    )
    db_session.add(kp)
    db_session.commit()
    assert kp.course_id == course.id
    assert kp.tags == ["file-system", "indexed-allocation"]


def test_create_profile_with_8_dimensions(db_session):
    user = User(username="test_user", password_hash="hashed", role="student")
    course = Course(name="OS", description="")
    db_session.add_all([user, course])
    db_session.commit()
    profile = StudentProfile(
        user_id=user.id,
        course_id=course.id,
        base_level="medium",
        learning_goal="掌握文件系统分配方式",
        knowledge_state="了解目录基础",
        weak_points=["链接分配", "索引分配"],
        mastered_points=["文件目录"],
        learning_preference=["图解", "例题"],
        cognitive_style="visual",
        time_budget="2天",
    )
    db_session.add(profile)
    db_session.commit()
    assert len(profile.weak_points) == 2
    assert profile.cognitive_style == "visual"
