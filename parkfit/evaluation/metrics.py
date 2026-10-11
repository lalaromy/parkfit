"""Binary-classification metrics (Bishop 2006; Murphy 2012) and a small helper to
aggregate confusion counts."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Confusion:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0
    items: list[dict] = field(default_factory=list)

    def add(self, predicted: bool, actual: bool, **info) -> None:
        if predicted and actual:
            self.tp += 1
        elif predicted and not actual:
            self.fp += 1
        elif not predicted and actual:
            self.fn += 1
        else:
            self.tn += 1
        self.items.append({"predicted": predicted, "actual": actual, **info})

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0

    @property
    def accuracy(self) -> float:
        n = self.tp + self.fp + self.fn + self.tn
        return (self.tp + self.tn) / n if n else 0.0

    @property
    def false_admission_rate(self) -> float | None:
        """Share of truly unsuitable cases the system let through (FP / (FP + TN)); the
        error that costs a driver a wasted trip."""
        return self.fp / (self.fp + self.tn) if self.fp + self.tn else None

    @property
    def specificity(self) -> float | None:
        return self.tn / (self.tn + self.fp) if self.tn + self.fp else None

    @property
    def balanced_accuracy(self) -> float | None:
        sp = self.specificity
        return (self.recall + sp) / 2 if sp is not None and self.tp + self.fn else None

    def summary(self) -> dict:
        r = lambda v: None if v is None else round(v, 3)
        return {"tp": self.tp, "fp": self.fp, "fn": self.fn, "tn": self.tn,
                "n": self.tp + self.fp + self.fn + self.tn,
                "positives": self.tp + self.fn, "negatives": self.fp + self.tn,
                "precision": round(self.precision, 3), "recall": round(self.recall, 3),
                "f1": round(self.f1, 3), "accuracy": round(self.accuracy, 3),
                "false_admission_rate": r(self.false_admission_rate),
                "balanced_accuracy": r(self.balanced_accuracy)}
