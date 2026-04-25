from memory.session_history import save_session
from memory.weak_topic_tracker import update_topic
from memory.preference_memory import save_preference


def update_memory_after_interaction(
    student_id,
    topic=None,
    summary=None,
    struggled=False,
    preference_signal=None
):
    if topic:
        update_topic(student_id, topic, struggled=struggled)

    if summary:
        save_session(student_id, topic, summary)

    if preference_signal:
        key = preference_signal.get("key")
        value = preference_signal.get("value")
        confidence = preference_signal.get("confidence", 1.0)

        if key and value:
            save_preference(student_id, key, value, confidence)