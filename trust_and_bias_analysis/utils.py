from pathlib import Path
from typing import Optional

import yaml
import pkgutil

def load_yaml(package: str, filename: str, local_path: Optional[Path] = None):
    try:
        data = pkgutil.get_data(package, filename)
        if data is None:
            raise FileNotFoundError(f"Resource {filename} not found in package {package}")
        return yaml.safe_load(data.decode("utf-8"))
    except Exception as e:
        if local_path and local_path.exists():
            with open(local_path, "r") as f:
                return yaml.safe_load(f)
        raise FileNotFoundError(f"Could not load {filename} from {package} or {local_path}") from e