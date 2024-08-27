from dataclasses import asdict, dataclass, field
from typing import Annotated

import pytest

from pucoti import config
from pucoti.config import Config


@dataclass(frozen=True)
class SmallConfig(Config):
    """A small config"""

    name: str = "Joe"
    age: Annotated[int, "Pass -1 if you don't want to tell"] = -1

    EXPECTED = """# A small config
name: Joe
# Pass -1 if you don't want to tell
age: -1"""


@dataclass(frozen=True)
class ConfigWithList(Config):
    """With lists"""

    names: list[str] = field(default_factory=list)
    rect: tuple[int, int] = (3, 4)

    EXPECTED = """
# With lists
names: []
rect: [3, 4]
"""


@dataclass(frozen=True)
class RecursiveConfig(Config):
    """Recursivity!"""

    small: SmallConfig = SmallConfig()
    lists: Annotated[ConfigWithList, "Annot for a sub-config"] = ConfigWithList()

    EXPECTED = """
# Recursivity!
small:
  # A small config
  name: Joe
  # Pass -1 if you don't want to tell
  age: -1
# Annot for a sub-config
lists:
  # With lists
  names: []
  rect: [3, 4]
"""


@pytest.mark.parametrize("cfg", [Config, SmallConfig, Annotated[Config, "annotation"]])
def test_is_config_yes(cfg):
    assert config.Config.is_config(cfg)


@pytest.mark.parametrize(
    "not_cfg",
    [
        list[Config],
        tuple[Config, Config],
        Annotated[int, "not ok"],
    ],
)
def test_is_config_no(not_cfg):
    assert not config.Config.is_config(not_cfg)


all_config_classes = pytest.mark.parametrize(
    "cfg",
    [
        SmallConfig,
        ConfigWithList,
        RecursiveConfig,
    ],
)


@all_config_classes
def test_gen_yaml(cfg):
    generated = cfg.generate_default_config_yaml().strip()
    print(generated)
    expected = cfg.EXPECTED.strip()
    assert generated == expected


@all_config_classes
def test_dump_load(cfg: type[Config]):
    default_config = cfg()
    assert cfg().load(asdict(default_config)) == default_config


def test_merge_simple():
    cfg = SmallConfig()

    new = cfg.merge(dict(age=12))

    assert asdict(new) == dict(age=12, name="Joe")
    # Should not have changed
    assert asdict(cfg) == asdict(SmallConfig())


def test_load_partial():
    new = RecursiveConfig().load({"small": {"age": 99}})

    assert asdict(new) == asdict(RecursiveConfig(small=SmallConfig(age=99)))
