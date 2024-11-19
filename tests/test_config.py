from typing import Annotated, ClassVar

from pydantic import Field

import pytest
import yaml

from pucoti import config
from pucoti.base_config import Config


class SmallConfig(Config):
    """A small config"""

    name: str = "Joe"
    age: Annotated[int, Field(description="Pass -1 if you don't want to tell")] = -1

    EXPECTED: ClassVar = """# A small config
name: Joe
# Pass -1 if you don't want to tell
age: -1"""


class ConfigWithList(Config):
    """With lists"""

    names: Annotated[list[str], Field(default_factory=list)]
    rect: tuple[int, int] = (3, 4)

    EXPECTED: ClassVar = """
# With lists
names: []
rect: [3, 4]
"""


class RecursiveConfig(Config):
    """Recursivity!"""

    small: SmallConfig = SmallConfig()
    lists: Annotated[ConfigWithList, Field(description="Annot for a sub-config")] = ConfigWithList()

    EXPECTED: ClassVar = """
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
    assert cfg().merge_partial(default_config.model_dump()) == default_config


def test_merge_simple():
    cfg = SmallConfig()

    new = cfg.merge_partial(dict(age=12))

    assert new.model_dump() == dict(age=12, name="Joe")
    # Should not have changed
    assert cfg.model_dump() == SmallConfig().model_dump()


def test_load_partial():
    new = RecursiveConfig().merge_partial({"small": {"age": 99}})

    assert new.model_dump() == RecursiveConfig(small=SmallConfig(age=99)).model_dump()


def test_load_template():
    template = config.PucotiConfig.generate_default_config_yaml()
    data = yaml.safe_load(template)

    cfg_validated = config.PucotiConfig.model_validate(data)
    cfg_merged = config.PucotiConfig().merge_partial(data)
    cfg_default = config.PucotiConfig()

    assert cfg_validated == cfg_default
    assert cfg_merged == cfg_default
