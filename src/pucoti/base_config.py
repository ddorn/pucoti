from pathlib import Path
from typing import Annotated, Any, Self, TypeAliasType, get_origin
from dataclasses import dataclass, fields, MISSING
from textwrap import dedent, indent

import yaml


AnnotatedType = type(Annotated[int, "dummy"])


@dataclass(frozen=True)
class Config:
    """The base class for configuration defined by dataclasses by the developer
    and modified using yaml by the user.


    This is not a battleproof implementation.
    In particular, it has no support for arbitrary dicts as values (only dataclasses aka. Config),
    limited support for lists and no support for custom types.
    Errors by users will likely raise understandable exceptions, but errors from devs will
    likely not, as the code with type hints is too messy and britle.
    """

    def load(self, conf: str | dict | Path) -> Self:
        if isinstance(conf, Path):
            data = yaml.safe_load(conf.read_text())
        elif isinstance(conf, str):
            data = yaml.safe_load(conf)
        else:
            data = conf

        # This is a bit messy, and I garantee that this function will not work for
        # evert `config_cls` thrown at it. It will work for most that use only
        # simple type hints. It will not work for unions nor dicts.
        # When it doesn't work because of unsupported config_cls, it will not
        # throw meaningful error messages, but if its `conf` input is invalid,
        # it does its best to throw a meaningful ValueError.

        def path_to_str(path, name: None | str = None):
            if name:
                path = path + (name,)
            return ".".join(path)

        to_update = {}

        def gather_updates(path: tuple, data, expected_type, is_inside_list=False):
            # If Annotated, strip the annotation
            if isinstance(expected_type, AnnotatedType):
                expected_type = expected_type.__origin__
            if isinstance(expected_type, TypeAliasType):
                expected_type = expected_type.__value__

            if Config.is_config(expected_type):
                fields_by_name = {field.name: field for field in fields(expected_type)}
                converted_data = {}
                for name, value in data.items():
                    if name not in fields_by_name:
                        valid_fields = ", ".join(fields_by_name)
                        raise ValueError(
                            f"Unknown field {path_to_str(path, name)}. Valid fields are {valid_fields}"
                        )
                    converted_data[name] = gather_updates(
                        path + (name,),
                        value,
                        fields_by_name[name].type,
                        is_inside_list=is_inside_list,
                    )

                return expected_type(**converted_data)

            elif get_origin(expected_type) in (list, tuple):
                if not isinstance(data, (list, tuple)):
                    raise ValueError(f"Expected a list at {path_to_str(path)}, got {data}")
                elif get_origin(expected_type) is tuple:
                    collection_type = tuple
                    sub_types = expected_type.__args__
                    if len(sub_types) != len(data):
                        raise ValueError(
                            f"Expected a tuple of size {len(sub_types)} at {path_to_str(path)}, got {len(data)}"
                        )
                else:
                    collection_type = list
                    sub_types = [expected_type.__args__[0]] * len(data)
                # There is no merging of lists/tuples, we overwrite the full list.
                converted_data = collection_type(
                    gather_updates(path + (i,), d, sub_types[i], is_inside_list=True)
                    for i, d in enumerate(data)
                )
                if not is_inside_list:
                    to_update[path] = converted_data
                return converted_data

            elif expected_type in (str, int, float, Path, bool):
                converted_data = expected_type(data)
                if not is_inside_list:
                    to_update[path] = converted_data
                return converted_data

            else:
                raise ValueError(f"Unsupported type {expected_type} at {path_to_str(path)}")

        gather_updates((), data, type(self))

        # Make the flat dict into a recursive one
        def unflatten(d):
            out = {}
            for path, value in d.items():
                obj = out
                for part in path[:-1]:
                    obj = obj.setdefault(part, {})
                obj[path[-1]] = value
            return out

        to_update = unflatten(to_update)

        return self.merge(to_update)

    @staticmethod
    def is_config(type_hint):
        if isinstance(type_hint, AnnotatedType):
            type_hint = type_hint.__origin__
        if not isinstance(type_hint, type):
            return False
        return issubclass(type_hint, Config)

    @classmethod
    def gather_parameters(cls, prefix: str = "") -> dict[str, type]:
        """Recursively gathers all attributes of the config, except the ones in lists."""
        params = {}
        for fld in fields(cls):
            if cls.is_config(fld.type):
                params.update(fld.type.gather_parameters(prefix + fld.name + "."))
            elif get_origin(fld.type) is list:
                base_type = fld.type.__args__[0]
                # If base_type can be prompted in a single are (like int, str, etc)
                # Then we can make this a parameter
                if base_type in (str, int, float, Path, bool):
                    params[prefix + fld.name] = fld.type

            elif get_origin(fld.type) is dict:
                pass
            else:
                params[prefix + fld.name] = fld.type

        return params

    @classmethod
    def user_defined_docstring(cls) -> str | None:
        """Return the docstring of the class, without the automatically generated part."""

        if cls.__doc__ and not cls.__doc__.startswith(cls.__name__ + "("):
            return cls.__doc__
        # Doc is automatically generated or non existant. We don't want to show that
        return None

    @classmethod
    def generate_default_config_yaml(cls) -> str:
        """Make the content of the yaml file with all parameters as default.

        It also shows the docsting for parameters as comments
        """

        out = []

        def add_comment(comment: str):
            out.append(indent(dedent(comment), "# "))

        if doc := cls.user_defined_docstring():
            add_comment(doc)

        for fld in fields(cls):
            try:
                doc = fld.type.__metadata__[0]
                out.append("\n")
                add_comment(doc)
            except AttributeError:
                pass

            if cls.is_config(fld.type):
                # assert issubclass(fld.type, Config)
                out.append("\n")
                out.append(f"{fld.name}:")
                out.append(indent(fld.type.generate_default_config_yaml(), "  "))
                continue

            if fld.default is not MISSING:
                default = fld.default
            elif fld.default_factory is not MISSING:
                default = fld.default_factory()
            else:
                raise ValueError(f"Field {fld.name} has no default value")

            out.append(to_nice_yaml(fld.name, default))

        return "\n".join(part.rstrip() for part in out)

    def merge(self, values: dict[str, dict | Any]):
        """Return a new config with the values provided replaced.

        Does not perform any validation of paths nor types. For this, use .load()
        """
        if isinstance(values, type(self)):
            return values

        kwargs = {}
        for field in fields(self):
            if field.name not in values:
                kwargs[field.name] = getattr(self, field.name)
            elif self.is_config(field.type):
                kwargs[field.name] = getattr(self, field.name).merge(values[field.name])
            else:
                kwargs[field.name] = values[field.name]

        return type(self)(**kwargs)

    def get(self, name: str):
        obj = self
        for part in name.split("."):
            obj = getattr(obj, part)
        return obj

    @classmethod
    def get_field(cls, name: str):
        """Recursively get the field at the given path."""

        obj = cls
        for part in name.split("."):
            field = next(fld for fld in fields(obj) if fld.name == part)
            obj = field.type
        return field

    @classmethod
    def doc_for(cls, name: str):
        """Return the docstring for the field at the given path."""

        field = cls.get_field(name)

        if get_origin(field.type) is list:
            typ = field.type.__args__[0]
        else:
            typ = field.type

        if isinstance(typ, AnnotatedType):
            return typ.__metadata__[0]
        elif cls.is_config(typ) and issubclass(typ, Config):  # second check if for mypy
            return typ.user_defined_docstring()

        return None


def to_nice_yaml(name: str, obj):
    if isinstance(obj, Path):
        obj = str(obj)
    elif isinstance(obj, tuple):
        obj = list(obj)

    # default_flow_style=True makes it a one-liner, so that colors don't take to much space
    # but it outputs {name: value}, so we need to remove the first { and last }
    out = yaml.dump({name: obj}, allow_unicode=True, default_flow_style=True)
    return out[1:-2]
