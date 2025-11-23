from __future__ import annotations

from agent.model.classifiers.clickbait_classifier import get_classifier as get_clickbait
from agent.model.classifiers.educational_classifier import get_classifier as get_educational
from agent.model.classifiers.thumbnail_classifier import get_classifier as get_thumbnail
from agent.model.classifiers.topic_classifier import get_classifier as get_topic


def load_classifiers():
    return {
        "clickbait": get_clickbait(),
        "educational": get_educational(),
        "topic": get_topic(),
        "thumbnail": get_thumbnail(),
    }
