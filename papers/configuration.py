import dataclasses
from pathlib import Path


@dataclasses.dataclass
class Configuration:
    root_directory: Path = Path.home() / '.papers'


configuration = Configuration()
