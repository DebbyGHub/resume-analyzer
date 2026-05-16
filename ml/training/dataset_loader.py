"""
dataset_loader.py

Loads question_bank.json and answer_variants.json, merges them by
question_id, and flattens into a list of ML-ready training samples.

Each sample:
{
    "question":          str,
    "ideal_answer":      str,
    "candidate_answer":  str,
    "label":             float,
    "quality":           str,
    "topic":             str,
    "difficulty":        str,
}
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths — relative to this file so no absolute paths are hardcoded
# ---------------------------------------------------------------------------

_DATASETS_DIR = Path(__file__).resolve().parent.parent / "datasets"
_QUESTION_BANK_PATH  = _DATASETS_DIR / "question_bank.json"
_ANSWER_VARIANTS_PATH = _DATASETS_DIR / "answer_variants.json"


# ---------------------------------------------------------------------------
# Dataclass for a single training sample
# ---------------------------------------------------------------------------

@dataclass
class TrainingSample:
    question:         str
    ideal_answer:     str
    candidate_answer: str
    label:            float
    quality:          str
    topic:            str
    difficulty:       str

    def to_dict(self) -> dict:
        return {
            "question":         self.question,
            "ideal_answer":     self.ideal_answer,
            "candidate_answer": self.candidate_answer,
            "label":            self.label,
            "quality":          self.quality,
            "topic":            self.topic,
            "difficulty":       self.difficulty,
        }


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_question_bank(path: Path = _QUESTION_BANK_PATH) -> dict[int, dict]:
    """
    Load question_bank.json and return a dict keyed by question_id.
    """
    if not path.exists():
        raise FileNotFoundError(f"question_bank not found: {path}")

    raw: list[dict] = json.loads(path.read_text(encoding="utf-8"))

    bank: dict[int, dict] = {}
    for entry in raw:
        qid = entry["id"]
        if qid in bank:
            logger.warning("Duplicate question_id %d in question_bank — skipping.", qid)
            continue
        bank[qid] = entry

    logger.info("Loaded %d questions from question_bank.", len(bank))
    return bank


def load_answer_variants(path: Path = _ANSWER_VARIANTS_PATH) -> dict[int, list[dict]]:
    """
    Load answer_variants.json and return a dict keyed by question_id.
    Each value is the list of answer dicts for that question.
    """
    if not path.exists():
        raise FileNotFoundError(f"answer_variants not found: {path}")

    raw: list[dict] = json.loads(path.read_text(encoding="utf-8"))

    variants: dict[int, list[dict]] = {}
    for entry in raw:
        qid = entry["question_id"]
        if qid in variants:
            logger.warning("Duplicate question_id %d in answer_variants — skipping.", qid)
            continue
        variants[qid] = entry["answers"]

    logger.info("Loaded answer variants for %d questions.", len(variants))
    return variants


# ---------------------------------------------------------------------------
# Merge + flatten
# ---------------------------------------------------------------------------

def merge_datasets(
    question_bank: dict[int, dict],
    answer_variants: dict[int, list[dict]],
) -> list[TrainingSample]:
    """
    Join question_bank and answer_variants on question_id.
    Skips question IDs present in one file but not the other.
    """
    samples: list[TrainingSample] = []
    missing_answers = 0
    missing_questions = 0

    for qid, question_data in question_bank.items():
        if qid not in answer_variants:
            logger.warning("question_id %d has no answer variants — skipping.", qid)
            missing_answers += 1
            continue

        for answer in answer_variants[qid]:
            samples.append(TrainingSample(
                question         = question_data["question"],
                ideal_answer     = question_data["ideal_answer"],
                candidate_answer = answer["candidate_answer"],
                label            = float(answer["label"]),
                quality          = answer["quality"],
                topic            = question_data["topic"],
                difficulty       = question_data["difficulty"],
            ))

    for qid in answer_variants:
        if qid not in question_bank:
            logger.warning("question_id %d in answer_variants has no question — skipping.", qid)
            missing_questions += 1

    if missing_answers or missing_questions:
        logger.warning(
            "Merge completed with %d missing answer sets and %d missing questions.",
            missing_answers, missing_questions,
        )

    logger.info("Merged dataset: %d training samples.", len(samples))
    return samples


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def load_training_samples() -> list[dict]:
    """
    Full pipeline: load → merge → flatten to list[dict].
    Returns 256 samples for the 64-question / 4-answer-per-question dataset.
    """
    question_bank    = load_question_bank()
    answer_variants  = load_answer_variants()
    samples          = merge_datasets(question_bank, answer_variants)
    return [s.to_dict() for s in samples]

if __name__ == "__main__":
    samples = load_training_samples()

    print(f"Loaded {len(samples)} training samples.\n")

    if samples:
        print("First sample:\n")
        print(samples[0])