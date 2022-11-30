from __future__ import annotations

import argparse
import logging

import torch
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger(__name__)


class Meter:
    """
    This class is used to keep track of the metrics in the train and dev loops.
    """

    def __init__(self, target_classes: list[int]) -> None:
        """
        :param target_classes: The classes for whom the metrics will be calculated.
        """
        self.target_classes = target_classes

        self.loss = 0

        self.micro_prec = 0
        self.micro_recall = 0
        self.micro_f1 = 0

        self.macro_prec = 0
        self.macro_recall = 0
        self.macro_f1 = 0

        self.it = 0

    def update_params(
        self, loss: float, logits: torch.Tensor, gold: torch.Tensor
    ) -> tuple[float, float, float, float, float, float, float]:
        """Update the metrics.

        :param loss: The current loss.
        :param logits: The current logits.
        :param y_true: The current true labels.
        :return: tuple of updated metrics: (loss, micro_prec, micro_recall,
            micro_f1, macro_prec, macro_recall, macro_f1)
        """
        # get the argmax of logits from each output
        y_pred = torch.tensor(
            [torch.argmax(x) for x in logits.view(-1, logits.shape[2])]
        ).tolist()
        y_true = gold.reshape(-1).tolist()

        new_pred = []
        new_true = []
        for i in range(len(y_pred)):
            if y_true[i] in self.target_classes:
                new_true.append(y_true[i])
                new_pred.append(y_pred[i])

        y_true = new_true
        y_pred = new_pred

        # compute the micro precision/recall/f1, macro precision/recall/f1
        micro_prec = precision_score(
            y_true,
            y_pred,
            labels=self.target_classes,
            average="micro",
            zero_division=0,  # type: ignore
        )
        micro_recall = recall_score(
            y_true,
            y_pred,
            labels=self.target_classes,
            average="micro",
            zero_division=0,  # type: ignore
        )
        micro_f1 = f1_score(
            y_true,
            y_pred,
            labels=self.target_classes,
            average="micro",
            zero_division=0,  # type: ignore
        )

        macro_prec = precision_score(
            y_true,
            y_pred,
            labels=self.target_classes,
            average="macro",
            zero_division=0,  # type: ignore
        )
        macro_recall = recall_score(
            y_true,
            y_pred,
            labels=self.target_classes,
            average="macro",
            zero_division=0,  # type: ignore
        )
        macro_f1 = f1_score(
            y_true,
            y_pred,
            labels=self.target_classes,
            average="macro",
            zero_division=0,  # type: ignore
        )

        self.loss = (self.loss * self.it + loss) / (self.it + 1)

        self.micro_prec = (self.micro_prec * self.it + micro_prec) / (self.it + 1)
        self.micro_recall = (self.micro_recall * self.it + micro_recall) / (self.it + 1)
        self.micro_f1 = (self.micro_f1 * self.it + micro_f1) / (self.it + 1)

        self.macro_prec = (self.macro_prec * self.it + macro_prec) / (self.it + 1)
        self.macro_recall = (self.macro_recall * self.it + macro_recall) / (self.it + 1)
        self.macro_f1 = (self.macro_f1 * self.it + macro_f1) / (self.it + 1)

        self.it += 1

        return (
            float(self.loss),
            float(self.micro_prec),
            float(self.micro_recall),
            float(self.micro_f1),
            float(self.macro_prec),
            float(self.macro_recall),
            float(self.macro_f1),
        )

    def reset(self) -> None:
        """Resets the metrics to the 0 values. Must be used after each epoch."""
        self.loss = 0

        self.micro_prec = 0
        self.micro_recall = 0
        self.micro_f1 = 0

        self.macro_prec = 0
        self.macro_recall = 0
        self.macro_f1 = 0

        self.it = 0


def print_info(
    target_classes: list[int],
    label_encoder: LabelEncoder,
    lang_model_name: str,
    fine_tune: bool,
    device: torch.device,
) -> None:
    print("Training session info:")
    print("\tLanguage model: {}, Finetune: {}".format(lang_model_name, fine_tune))
    print(
        "\tTarget classes: {}".format(
            [
                label_encoder.inverse_transform([target_class])[0]
                for target_class in target_classes
            ]
        )
    )
    print("\tAll classes: {}".format(label_encoder.classes_.tolist()))  # type: ignore
    print("\tDevice: {}".format(device))


def dump_args(args: argparse.Namespace) -> None:
    print("Arguments")
    print("---------")
    for key, value in vars(args).items():
        print(f"{key}: {value}")
    print()
