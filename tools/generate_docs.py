import argparse
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET


@dataclass
class MavMessageField:
    name: str
    type: str
    description: str = ""
    enum: str | None = None
    units: str | None = None


@dataclass
class MavMessage:
    id: int
    name: str
    description: str = ""
    fields: list[MavMessageField] = field(default_factory=list)
    source: Path = ""


@dataclass
class EnumEntry:
    value: int
    name: str
    description: str = ""


@dataclass
class MavEnum:
    name: str
    description: str = ""
    entries: list[EnumEntry] = field(default_factory=list)
    source: Path = ""

@dataclass
class Dialect:
    name: str
    messages: list[MavMessage]
    enums: list[MavEnum]
    description: str = ""

def text(element: ET.Element | None) -> str:
    if element is None:
        return ""

    return "".join(element.itertext()).strip()


def parse_xml(path: Path) -> Dialect:
    root = ET.parse(path).getroot()

    messages: list[MavMessage] = []
    enums: list[MavEnum] = []

    for element in root.findall(".//message"):
        message = MavMessage(
            id=int(element.attrib["id"]),
            name=element.attrib["name"],
            description=text(element.find("description")),
            source=path
        )

        for field_element in element.findall("field"):
            message.fields.append(
                MavMessageField(
                    name=field_element.attrib["name"],
                    type=field_element.attrib["type"],
                    description=text(field_element),
                    enum=field_element.attrib.get("enum"),
                    units=field_element.attrib.get("units"),
                )
            )

        messages.append(message)

    for element in root.findall(".//enum"):
        enum = MavEnum(
            name=element.attrib["name"],
            description=text(element.find("description")),
            source=path
        )

        for entry_element in element.findall("entry"):
            enum.entries.append(
                EnumEntry(
                    value=int(entry_element.attrib["value"]),
                    name=entry_element.attrib["name"],
                    description=text(entry_element.find("description")),
                )
            )

        enums.append(enum)

    return Dialect(name=path.name,description="",messages=messages, enums=enums)

def tidyDescription(desc_string, type:str):
    """
    Helper method to remove odd whitespace etc from a description string.
    Different behaviour if the string is to be used in normal markdown or in a table.
    """
    if "\n" not in desc_string:
        desc_string = desc_string.strip()
        return desc_string
    if type == "markdown":
        desc = desc_string
        desc.strip()
        lines = desc.splitlines()
        first_line = lines[0].strip()
        new_string = first_line + "\n\n"
        for line in lines[1:]:
            new_string += line.strip() + "\n"
        desc_string = new_string.strip()
        return desc_string
    if type == "table":
        lines = desc_string.strip().splitlines()
        new_string = "<br/>".join(line.strip() for line in lines)
        return new_string.strip()

def render_message(message: MavMessage) -> str:
    lines = [
        f"## {message.name} ({message.id}) - [from [{message.source.name}](../dialects/{message.source.stem}.md)]",
        "",
    ]

    if message.description:
        lines += [
            tidyDescription(message.description,type="markdown"),
            "",
        ]

    lines += [
        "| Field Name | Type | Units | Values | Description |",
        "|---|---|---|---|---|",
    ]

    for field in message.fields:
        description = tidyDescription(field.description,type="table")

        lines.append(
            f"| `{field.name}` | `{field.type}` | {f"`{field.units}`" if field.units else ""} | {f"[{field.enum}](../enums/{field.enum}.md)" if field.enum else ""} | {description} |"
        )

    lines.append("")

    return "\n".join(lines)


def render_enum(enum: MavEnum) -> str:
    lines = [
        f"## {enum.name} - [from [{enum.source.name}](../dialects/{enum.source.stem}.md)]",
        "",
    ]

    if enum.description:
        lines += [
            tidyDescription(enum.description,type="markdown"),
            "",
        ]

    lines += [
        "| Value | Name | Description |",
        "|---:|---|---|",
    ]

    for entry in enum.entries:
        description = tidyDescription(entry.description,type="table")

        lines.append(
            f"| {entry.value} | `{entry.name}` | {description} |"
        )

    lines.append("")

    return "\n".join(lines)

def render_dialect(dialect: Dialect)->str:
    lines = [
        f"# {dialect.name}",
         "",
         "## Messages",
         ""
    ]
    lines.extend(
        [f"- [{message.name}](../messages/{message.name}.md)" for message in dialect.messages]
    )
    lines.extend([
        "",
        "## Enumerated Types",
        ""
    ])
    lines.extend(
        [f"- [{enum.name}](../enums/{enum.name}.md)" for enum in dialect.enums]
    )
    return "\n".join(lines)

def generate(
    inputs: list[Path],
    output: Path,
) -> None:
    messages: list[MavMessage] = []
    enums: list[MavEnum] = []

    dialect_dir = output / "dialects"
    messages_dir = output / "messages"
    enums_dir = output / "enums"

    dialect_dir.mkdir(parents=True, exist_ok=True)
    messages_dir.mkdir(parents=True, exist_ok=True)
    enums_dir.mkdir(parents=True, exist_ok=True)

    for path in inputs:
        for filepath in path.glob("*.xml"):
            dialect = parse_xml(filepath)
            messages.extend(dialect.messages)
            enums.extend(dialect.enums)
            (dialect_dir / f"{filepath.stem}.md").write_text(
                render_dialect(dialect),
                encoding="utf-8"
            )


    for message in messages:
        (messages_dir / f"{message.name}.md").write_text(
            render_message(message),
            encoding="utf-8",
        )

    for enum in enums:
        (enums_dir / f"{enum.name}.md").write_text(
            render_enum(enum),
            encoding="utf-8",
        )

def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("docs"),
    )

    args = parser.parse_args()

    generate(args.inputs, args.output)


if __name__ == "__main__":
    main()