# MAVLink Dialect

本repositoryは、Avionics Systemで使用するMAVLink dialectを管理する。

MAVLinkは、Node間で交換するmessageを定義し、異なるfirmwareおよび外部システム間で共通のデータ形式を使用するための通信プロトコルである。本repositoryでは、システム固有のMAVLink messageを定義し、その定義を各firmwareおよび外部システムで共有する。

## Repository Structure

```text
mavlink-dialect/
├── dialect/
│   └── *.xml
├── docs/
│   ├── architecture.md
│   └── development.md
├── tests/
├── tools/
├── .github/
│   └── workflows/
└── README.md
```

`dialect/`にはMAVLink messageの定義を配置する。

`docs/`には、本repositoryのarchitectureおよびdevelopment processに関する文書を配置する。

`tests/`には、dialectおよび生成物を検証するためのtestを配置する。

`tools/`には、developmentおよびvalidationを補助するtoolを配置する。

`.github/workflows/`には、Continuous Integrationおよびその他のautomationに使用するGitHub Actions workflowを配置する。

## Documentation

本repositoryの設計および開発方法については、以下のdocumentを参照する。

* [Architecture](docs/architecture.md) — システム構成、Protocol Architecture、Message ArchitectureおよびExternal Interfaces
* [Development](docs/development.md) — 開発workflow、code generation、validation、CI、dependency managementおよびrelease process

## Usage

MAVLink messageを追加または変更する場合は、`dialect/`にあるMAVLink dialect definitionを変更する。

変更されたdialectはCIによって検証され、MAVLink generatorによるcode generationおよび生成されたC++ codeのvalidationが実行される。

生成されたC++ libraryは、下流repositoryである`mavlink-cpp`から利用する。

```text
mavlink-dialect
       │
       │ MAVLink Message Definition
       ▼
mavlink-cpp
       │
       │ Generated C++ Library
       ▼
Firmware / External Systems
```

各firmwareは、原則として生成された`mavlink-cpp`をdependencyとして利用する。MAVLink messageのserializationおよびdeserializationをfirmware側で独自に実装してはならない。

## Design Principles

本repositoryでは、以下の原則に従ってMAVLink dialectを管理する。

- MAVLink messageの定義を単一のsource of truthとして管理する。
- Messageの構造および意味を明確に定義する。
- MAVLink messageの定義とTransportの実装を分離する。
- 生成されたcodeを手動で変更しない。
- Message definitionの変更をCIによって検証する。
- 下流repositoryではversion付きの生成libraryを利用する。

詳細な設計方針については[Architecture](docs/architecture.md)を参照する。

## Development

開発環境の構築、messageの追加方法、code generation、validation、CIおよびreleaseについては[Development](docs/development.md)を参照する。

Pull Requestを作成した場合、CIによってdialectのvalidationおよびgenerated codeの検証が実行される。