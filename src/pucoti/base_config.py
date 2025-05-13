from pathlib import Path
from pydantic import BaseModel, ConfigDict
from textwrap import dedent, indent
from typing import Any, Self
import yaml


class Config(BaseModel):
    _filepath: Path | None = None

    model_config = ConfigDict(
        # frozen=True,
        extra="forbid",
    )

    def merge_partial(self, values: dict[str, dict | Any]) -> Self:
        updates = self.__class__.model_validate(values)
        to_update = updates.model_fields_set
        copy_args = {}
        for key in to_update:
            current_value = getattr(self, key)
            new_value = getattr(updates, key)
            if isinstance(current_value, Config):
                new_value = current_value.merge_partial(values[key])
                copy_args[key] = new_value
            elif isinstance(current_value, (tuple, list)):
                copy_args[key] = new_value
            else:
                copy_args[key] = new_value
        return self.model_copy(update=copy_args)

    def merge_partial_from_file(self, filepath: Path) -> Self:
        with open(filepath) as f:
            values = yaml.safe_load(f)
        return self.merge_partial(values)

    @classmethod
    def generate_default_config_yaml(cls) -> str:
        """Make the content of the yaml file with all parameters as default.

        It also shows the Field.description for parameters as comments.
        """

        defaults = cls()

        lines_out = []

        def add_comment(comment: str):
            lines_out.append(indent(dedent(comment), "# "))

        if doc := cls.__doc__:
            add_comment(doc)

        for name, fld in cls.model_fields.items():
            if name.startswith("_"):
                continue

            doc = fld.description
            if doc is not None:
                add_comment(doc)

            if isinstance(getattr(defaults, name), Config):
                lines_out.append(f"{name}:")
                lines_out.append(
                    indent(getattr(defaults, name).generate_default_config_yaml(), "  ")
                )
                continue

            default = fld.get_default(call_default_factory=True)
            lines_out.append(to_nice_yaml(name, default))

        return "\n".join(part.rstrip() for part in lines_out)

    @classmethod
    def doc_for(cls, name: str) -> str | None:
        """Return the docstring for a specific parameter."""

        parts = name.split(".")
        field = cls.model_fields[parts[0]]
        for part in parts[1:]:
            annot = field.annotation
            # field.annotation is necessarly a subconfig. It doesn't have an meaning otherwise
            assert isinstance(annot, type)
            assert issubclass(annot, Config)
            field = annot.model_fields[part]

        if field.description is not None:
            return field.description
        try:
            return field.annotation.__doc__
        except AttributeError:
            return None


def to_nice_yaml(name: str, obj):
    if isinstance(obj, Path):
        obj = str(obj)
    elif isinstance(obj, tuple):
        obj = list(obj)

    # default_flow_style=True makes it a one-liner, so that i.e. colors don't take to much space
    # but it outputs {name: value}, so we need to remove the first { and last }
    out = yaml.dump({name: obj}, allow_unicode=True, default_flow_style=True)
    return out[1:-2]
