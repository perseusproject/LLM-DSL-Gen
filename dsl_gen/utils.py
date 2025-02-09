import logging
from types import SimpleNamespace

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('dsl_gen')


class SafeNamespace(SimpleNamespace):
    """Namespace that masks sensitive information when printed, with multiline indentation."""

    def __repr__(self) -> str:
        return self._safe_repr()

    def __str__(self) -> str:
        return self._safe_repr()

    def _safe_repr(self, indent_level: int = 0) -> str:
        indent_str = "    " * indent_level
        child_indent_str = "    " * (indent_level + 1)

        lines = []
        lines.append(f"{indent_str}namespace(")

        items = []
        for k, v in self.__dict__.items():
            if isinstance(v, SafeNamespace):
                sub_repr = v._safe_repr(indent_level + 1)
                sub_lines = sub_repr.split("\n")

                if sub_lines:
                    sub_lines[0] = sub_lines[0].lstrip()

                final_sub_repr = "\n".join(sub_lines)
                items.append(f"{child_indent_str}{k}={final_sub_repr}")
            else:
                if k.lower() == "api_key":
                    items.append(f"{child_indent_str}{k}='****'")
                else:
                    items.append(f"{child_indent_str}{k}={repr(v)}")
        if items:
            lines.extend(items)
        lines.append(f"{indent_str})")
        return "\n".join(lines)

    def to_dict(self):
        """
        Convert the SafeNamespace to a dictionary, masking 'api_key' fields.
        """
        result = {}
        for k, v in self.__dict__.items():
            if isinstance(v, SafeNamespace):
                result[k] = v.to_dict()
            else:
                if k.lower() == "api_key":
                    result[k] = '****'
                else:
                    result[k] = v
        return result


def set_seed(seed):
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import random
        random.seed(seed)
    except ImportError:
        pass

    logger.info(f"Setting seed: {seed}")


__all__ = ["set_seed"]
