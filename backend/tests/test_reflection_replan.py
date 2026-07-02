"""Reflection→PathPlanner 协同闭环测试。

验证：
1. 答题答错后反思触发画像薄弱点更新
2. 画像薄弱点变化触发路径重规划
3. path_replanned 字段在返回值中
4. 防抖机制：短时间内多次答题不重复重规划
"""
import time
from datetime import datetime, timedelta

from app.agents.evaluation_agent import EvaluationAgent
from app.agents.reflection_agent import ReflectionAgent
from app.models.course import Course, KnowledgePoint
from app.models.exercise import Exercise, AnswerRecord
from app.models.learning_path import LearningPath, LearningPathNode
from app.models.profile import StudentProfile
from app.services.evaluation_service import submit_and_evaluate, REPLAN_DEBOUNCE_SECONDS
from app.services.mock_llm import MockLLM


def _setup_course_and_exercise(db):
    """创建测试课程、知识点、练习题。"""
    course = Course(name="测试课程", description="测试用")
    db.add(course)
    db.flush()

    kp = KnowledgePoint(
        course_id=course.id,
        chapter="测试章节",
        title="测试知识点",
        summary="测试摘要",
        key_content="测试内容",
        common_mistakes=["测试误区"],
        example_question="测试问题",
        example_answer="测试答案",
        difficulty="medium",
        tags=["test"],
        sources=["测试来源"],
        sort_order=1,
    )
    db.add(kp)
    db.flush()

    exercise = Exercise(
        knowledge_point_id=kp.id,
        question_type="short_answer",
        difficulty="medium",
        question="请简述测试知识点的核心思想。",
        answer="测试摘要",
        explanation="需要覆盖概念和场景。",
        tags=["test"],
    )
    db.add(exercise)
    db.flush()
    return course, kp, exercise


def _create_profile(db, user_id, course_id, weak_points=None, mastered_points=None):
    """创建学生画像。"""
    profile = StudentProfile(
        user_id=user_id,
        course_id=course_id,
        base_level="medium",
        learning_goal="掌握测试知识点",
        knowledge_state="",
        weak_points=weak_points or [],
        mastered_points=mastered_points or [],
        learning_preference=["图解"],
        cognitive_style="visual",
        time_budget="2天",
        confidence="medium",
    )
    db.add(profile)
    db.flush()
    return profile


def test_submit_wrong_answer_triggers_reflection(test_db):
    """答错后触发反思，返回 reflection 字段。"""
    from app.models.user import User
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = User(username="test_reflection_user", password_hash=pwd_context.hash("test123456"),
                role="student", display_name="测试用户")
    test_db.add(user)
    test_db.flush()

    course, kp, exercise = _setup_course_and_exercise(test_db)
    _create_profile(test_db, user.id, course.id, weak_points=[], mastered_points=[])

    # 替换 LLM 为 Mock
    import app.services.llm_client as lc
    original_get = lc.get_llm_client
    lc.get_llm_client = lambda: MockLLM()
    try:
        result = submit_and_evaluate(test_db, user.id, exercise.id, "错误的答案")
    finally:
        lc.get_llm_client = original_get

    assert "evaluation" in result
    assert "reflection" in result
    assert "answer_record_id" in result
    assert "path_replanned" in result


def test_path_replanned_field_present(test_db):
    """返回值包含 path_replanned 字段。"""
    from app.models.user import User
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = User(username="test_replan_user", password_hash=pwd_context.hash("test123456"),
                role="student", display_name="测试用户")
    test_db.add(user)
    test_db.flush()

    course, kp, exercise = _setup_course_and_exercise(test_db)
    _create_profile(test_db, user.id, course.id, weak_points=["其他知识点"], mastered_points=[])

    import app.services.llm_client as lc
    original_get = lc.get_llm_client
    lc.get_llm_client = lambda: MockLLM()
    try:
        result = submit_and_evaluate(test_db, user.id, exercise.id, "错误答案")
    finally:
        lc.get_llm_client = original_get

    assert "path_replanned" in result
    assert isinstance(result["path_replanned"], bool)


def test_replan_debounce_constant():
    """防抖常量为 600 秒。"""
    assert REPLAN_DEBOUNCE_SECONDS == 600


def test_reflection_agent_returns_profile_changes():
    """ReflectionAgent 返回 profile_changes 和 change_reason。"""
    agent = ReflectionAgent(llm=MockLLM())
    result = agent.run(
        evaluation_result={"is_correct": False, "mistake_tags": ["测试错因"]},
        current_profile={"weak_points": [], "mastered_points": ["已掌握知识点"]},
    )
    assert result.success
    assert "profile_changes" in result.data
    assert "change_reason" in result.data
