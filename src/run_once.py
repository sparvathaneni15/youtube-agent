import logging

from agent.pipeline import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def main():
    accepted = run_pipeline()
    logging.info("Accepted %d videos", len(accepted))
    for vid in accepted:
        logging.info("Accepted: %s (score=%.3f)", vid.get("title"), vid.get("value_score", 0.0))


if __name__ == "__main__":
    main()
