from typing import Dict


class Formatter:
    @staticmethod
    def format_markdown(bundle: Dict[str, str]) -> str:
        output = []
        for file_path, content in bundle.items():
            # match fixture markdown format exactly
            output.append(f"```python\n# {file_path}\n{content}\n```")
        return "\n\n".join(output) + "\n"

    @staticmethod
    def format_xml(bundle: Dict[str, str]) -> str:
        output = []
        for file_path, content in bundle.items():
            output.append(f'<file path="{file_path}">\n<content>\n{content}\n</content>\n</file>')
        return "\n\n".join(output) + "\n"

    @staticmethod
    def format_plain(bundle: Dict[str, str]) -> str:
        output = []
        for file_path, content in bundle.items():
            output.append(f"--- {file_path} ---\n{content}")
        return "\n\n".join(output) + "\n"

    @classmethod
    def format(cls, bundle: Dict[str, str], format_type: str = "markdown") -> str:
        if format_type == "xml":
            return cls.format_xml(bundle)
        elif format_type == "plain":
            return cls.format_plain(bundle)
        return cls.format_markdown(bundle)
