import tempfile
from pathlib import Path

import pytest

from launch.lib.service.common import list_jinja_templates


def create_temp_jinja_file(directory: Path, sub_path: str, content: str = ""):
    full_path = directory / sub_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)
    return full_path


@pytest.fixture
def setup_jinja_templates():
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        create_temp_jinja_file(base_dir, "templates/service/config.j2", "{{ config }}")
        create_temp_jinja_file(
            base_dir,
            "templates/service/{{ environment }}/database.j2",
            "{{ database }}",
        )
        yield base_dir


def test_list_jinja_templates(setup_jinja_templates):
    base_dir = setup_jinja_templates
    template_paths, modified_paths = list_jinja_templates(str(base_dir))

    assert len(template_paths) == 2
    assert len(modified_paths) == 2
    assert any("templates/service/*/database.j2" in path for path in modified_paths)
    assert all(path.startswith("templates/") for path in modified_paths)
    assert all(base_dir.as_posix() in path for path in template_paths)
