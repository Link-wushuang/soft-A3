from sqlalchemy.orm import Session

from app.agents.path_planner_agent import PathPlannerAgent
from app.models.course import KnowledgePoint
from app.models.learning_path import LearningPath, LearningPathNode
from app.models.profile import StudentProfile


def generate_learning_path(db: Session, user_id: int, course_id: int) -> LearningPath:
    agent = PathPlannerAgent()

    profile = db.query(StudentProfile).filter_by(user_id=user_id, course_id=course_id).first()
    profile_dict: dict = {}
    if profile:
        profile_dict = {
            "base_level": profile.base_level,
            "weak_points": profile.weak_points,
            "mastered_points": profile.mastered_points,
            "learning_goal": profile.learning_goal,
            "time_budget": profile.time_budget,
            "learning_preference": profile.learning_preference,
        }

    kps = db.query(KnowledgePoint).filter_by(course_id=course_id).order_by(
        KnowledgePoint.sort_order
    ).all()
    kp_titles = [kp.title for kp in kps]
    kp_map = {kp.title: kp.id for kp in kps}

    result = agent.run(profile=profile_dict, knowledge_points=kp_titles)
    if not result.success:
        raise RuntimeError(f"PathPlannerAgent failed: {result.error}")

    old_path = db.query(LearningPath).filter_by(
        user_id=user_id, course_id=course_id, status="active"
    ).first()
    if old_path:
        old_path.status = "replaced"

    path = LearningPath(user_id=user_id, course_id=course_id, status="active")
    db.add(path)
    db.flush()

    for i, node_data in enumerate(result.data.get("nodes", [])):
        title = node_data["knowledge_point_title"]
        kp_id = _match_kp(title, kp_map)
        if kp_id is None:
            continue
        node = LearningPathNode(
            path_id=path.id,
            knowledge_point_id=kp_id,
            sort_order=i,
            status="pending",
            reason=node_data.get("reason", ""),
        )
        db.add(node)

    db.commit()
    db.refresh(path)
    return path


def _match_kp(title: str, kp_map: dict[str, int]) -> int | None:
    """Match a knowledge point title to its ID, with fuzzy fallback."""
    if title in kp_map:
        return kp_map[title]
    for kp_title, kid in kp_map.items():
        if title in kp_title or kp_title in title:
            return kid
    return None
