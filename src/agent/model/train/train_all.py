from __future__ import annotations

from agent.model.train import train_clickbait, train_educational, train_topic, train_thumbnail


def main():
    train_clickbait.main()
    train_educational.main()
    train_topic.main()
    train_thumbnail.main()


if __name__ == "__main__":
    main()
