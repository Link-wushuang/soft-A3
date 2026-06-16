import json
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models import Course, Exercise, KnowledgePoint, KnowledgeSource, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _seed_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "os_course_seed.json"


def _default_mistakes(title: str) -> list[str]:
    return [f"混淆{title}的适用场景", f"遗漏{title}相关计算步骤"]


def _make_exercise(kp: KnowledgePoint, variant: int) -> Exercise:
    if variant == 0:
        return Exercise(
            knowledge_point_id=kp.id,
            question_type="short_answer",
            difficulty=kp.difficulty,
            question=f"请简述{kp.title}的核心思想，并说明一个常见误区。",
            answer=f"{kp.summary} 常见误区包括：{kp.common_mistakes[0]}。",
            explanation=f"回答需同时覆盖概念、适用场景和误区，不能只背定义。",
            tags=kp.tags,
        )
    return Exercise(
        knowledge_point_id=kp.id,
        question_type="choice",
        difficulty=kp.difficulty,
        question=f"关于{kp.title}，下列说法最准确的是哪一项？",
        options=[
            "只需要记住名称即可",
            kp.summary,
            "该知识点与操作系统无关",
            "所有场景都应使用同一种策略",
        ],
        answer=kp.summary,
        explanation=f"{kp.title}需要结合概念、机制和场景理解。",
        tags=kp.tags,
    )


def init_demo_data(db: Session) -> None:
    if db.query(User).filter(User.username == "demo_student").first():
        return

    seed = json.loads(_seed_path().read_text(encoding="utf-8"))
    db.add_all(
        [
            User(
                username="demo_student",
                password_hash=pwd_context.hash("demo123456"),
                role="student",
                display_name="演示学生",
            ),
            User(
                username="demo_teacher",
                password_hash=pwd_context.hash("teacher123456"),
                role="teacher",
                display_name="演示教师",
            ),
        ]
    )

    course = Course(name=seed["course"]["name"], description=seed["course"]["description"])
    db.add(course)
    db.flush()

    all_kps: list[KnowledgePoint] = []
    sort_order = 1
    for chapter in seed["chapters"]:
        db.add(
            KnowledgeSource(
                course_id=course.id,
                chapter=chapter["name"],
                source_name=chapter["source"],
                source_url="",
            )
        )
        for item in chapter["knowledge_points"]:
            kp = KnowledgePoint(
                course_id=course.id,
                chapter=chapter["name"],
                title=item["title"],
                summary=item["summary"],
                key_content=item["key_content"],
                common_mistakes=item.get("common_mistakes") or _default_mistakes(item["title"]),
                example_question=f"{item['title']}通常解决什么问题？",
                example_answer=item["summary"],
                difficulty=item["difficulty"],
                tags=item["tags"],
                sources=[chapter["source"]],
                case_materials=item.get("case_materials", ""),
                sort_order=sort_order,
            )
            sort_order += 1
            db.add(kp)
            all_kps.append(kp)

    db.flush()

    for kp_index, kp in enumerate(all_kps):
        db.add(_make_exercise(kp, 0))
        if kp_index < 22:
            db.add(_make_exercise(kp, 1))

    db.commit()
