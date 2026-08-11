# Development

本documentでは、`mavlink-dialect`の開発、変更、検証およびreleaseに関する手順と規則を定める。

`mavlink-dialect`は、他のrepositoryから参照されるMAVLink messageの定義を提供するため、変更内容が生成されるライブラリやそれを利用するfirmwareに影響する。したがって、message definitionの変更は、CIによる自動検証と生成物の更新を通じて管理する。

## Development Workflow

`mavlink-dialect`への変更は、原則としてPull Requestを通じて行う。main branchへ直接変更をpushしてはならない。

変更を行う場合は、まず変更内容をcommitとして作成し、Pull Requestを作成する。Pull Requestでは、変更されたmessage、変更理由、および既存のmessageや外部システムへの影響を確認する。

Pull Requestのmergeは、必要なCI checksが成功した後に行う。

Message definitionの変更では、単にXMLの構文が正しいことだけでなく、生成されるMAVLink libraryおよび既存のmessageとの整合性を確認する。

## Repository Structure

本repositoryでは、MAVLink dialectの定義と、それに関連するschema、documentation、CI configurationなどを管理する。

代表的なrepository structureを以下に示す。

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

`dialect/`にはMAVLink messageの定義を配置する。`docs/`には本repositoryのarchitectureおよびdevelopmentに関する文書を配置する。

Message definitionを検証するためのtestや補助的なtoolが必要な場合は、それぞれ`tests/`および`tools/`に配置する。

CI configurationは`.github/workflows/`で管理する。

実際のdirectory structureは、repositoryの規模および運用方法に応じて変更してよい。ただし、message definition、documentation、testおよびdevelopment infrastructureの責務が明確に分離されることを基本とする。

## Message Development

新しいMAVLink messageを追加する場合、既存のmessageで要求を満たせないことを確認した上で追加する。

Messageを追加または変更する際には、少なくとも以下を明確にする。

- messageの目的
- PublisherおよびSubscriber
- 各fieldの意味
- fieldの型
- 単位
- 有効な値の範囲
- 必要に応じてtimestamp、validityおよびstatus

既存messageの意味を変更する変更は、既存のPublisherおよびSubscriberの動作に影響するため、原則として新しいmessageの追加によって対応する。

Messageの命名、fieldの命名、型、単位およびその他のmessage design rulesは、`Message Architecture`および関連するmessage specificationに従う。

## Code Generation

MAVLink dialectから利用可能なライブラリを生成する場合、生成処理にはMAVLink公式のcode generatorである`mavgen`を使用する。

生成処理に使用する`mavgen`のversionは明示的に管理し、異なるversionによって生成結果が変化する場合でも、その変更を追跡できるようにする。

生成されたC++ codeは、`mavlink-dialect`におけるmessage definitionから再現可能でなければならない。生成物を手動で変更してはならない。

生成されたC++ libraryは、原則として`mavlink-cpp` repositoryで管理する。`mavlink-dialect`では、生成に必要な入力およびgeneration processを管理し、生成物そのものをsource of truthとはしない。

## Validation

MAVLink dialectの変更は、以下の観点から検証する。

まず、MAVLink dialectが正しいXMLおよびMAVLink dialectとして解釈可能であることを確認する。

次に、`mavgen`によるcode generationが正常に完了することを確認する。

さらに、生成されたlibraryがC++ compilerによって正常にcompileできることを確認する。

必要に応じて、messageのserializationおよびdeserializationが一致することをtestする。

Validationでは、少なくとも以下を自動的に検証する。

```text
Dialect
  │
  ├── XML / dialect validation
  │
  ├── mavgen
  │
  ├── Generated code compilation
  │
  └── Serialization / deserialization tests
```

これらの検証は、開発者のローカル環境だけでなくCIでも実行する。

## Continuous Integration

CIは、Pull Requestおよびmain branchへの変更に対して実行する。

Pull Requestでは、message definitionの構文検証、code generation、generated codeのcompileおよびtestを実行し、変更によって生成処理が壊れていないことを確認する。

main branchでは、Pull Requestで実行するvalidationに加えて、必要に応じて生成物の更新およびrelease processを実行する。

CIで使用するMAVLink generator、compilerおよびその他のdevelopment dependenciesはversionを固定または明示的に管理し、同一のcommitから同一の結果を再現できることを基本とする。

CI configurationそのものもrepositoryのsource codeとして管理する。

## Dependency Management

本repositoryが利用する外部dependencyは、可能な限りversionを明示して管理する。

特にMAVLink generatorである`mavgen`は生成物に直接影響するため、使用するversionを明示する。

Dependencyの更新にはRenovateを利用し、更新可能なdependencyを自動的に検出する。Renovateによる更新Pull Requestについても、通常のPull Requestと同じCI validationを実行する。

Dependencyの更新によってgenerated codeが変更される場合は、その変更内容を確認した上でmergeする。

## Release Process

`mavlink-dialect`のreleaseは、特定のmessage definitionおよびcode generation environmentの組み合わせを再現できる単位として管理する。

Release時には、少なくとも以下を記録する。

- dialect version
- 使用したMAVLink generatorのversion
- generated libraryとの対応
- 変更されたmessage
- compatibilityに影響する変更

Releaseされたdialectは、下流repositoryが依存するversionとして利用できる。

`mavlink-cpp`などの下流repositoryでは、releaseされたdialectをversion付きdependencyとして参照する。これにより、dialectの変更が各firmwareへ意図せず伝播することを防ぐ。

Release processは可能な限りCIによって自動化し、手動操作による生成物やversion情報の不整合を防止する。
