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

ディレクトリ構成を以下に示す。

```text
mavlink-dialect/
├── dialect/
│   └── *.xml
├── docs/
├── tools/
├── .github/
│   └── workflows/
└── README.md
```

`dialect/`にはMAVLink messageの定義を配置する。`docs/`には本repositoryのarchitectureおよびdevelopmentに関する文書を配置する。

Message definitionを検証するためのtestや補助的なtoolが必要な場合は、それぞれ`tests/`および`tools/`に配置する。

CI configurationは`.github/workflows/`で管理する。

実際のdirectory structureは、repositoryの規模および運用方法に応じて変更してよい。ただし、message definition、documentation、testおよびdevelopment infrastructureの責務が明確に分離されることを基本とする。

## Message Architecture

本システムでは、Node間で交換する情報をMAVLink messageとして定義します。MAVLink messageは、単一の情報を表現するためにできるだけ小さな単位に分割して設計します。MAVLink messageの具体的な構造は`mavlink-dialect`で定義します。本章では、messageを設計および運用する際の共通規則を定めます。

### Messageの決め方の原則

MAVLink messageは、以下の原則に従って設計します。

1. 1つのmessageは明確に定義された一つの目的を持つものとする。異なる目的の情報を一つのmessageにまとめることで、messageの意味や利用条件が曖昧にならないようにする。
1. fieldの意味および単位を明確に定義する。物理量を表すfieldについては、原則としてSI単位系を使用する。単位だけでなく、必要に応じてスケール、符号、基準座標系および有効範囲を定義する。
1. messageの受信側がmessage単体から必要な情報を解釈できるようにする。外部文書や特定のfirmware実装を前提としなければ意味を解釈できないmessage設計は避ける。
1. messageの変更による互換性への影響を考慮する。既存messageのfieldを変更または削除する場合は、既存のPublisherおよびSubscriberへの影響を評価する。互換性に関する具体的な規則は、Compatibility and Versioningで定義する。

### Messageの有効性

MAVLink messageの各fieldには、値が有効である条件を必要に応じて定義します。

MeasurementやStateなどのmessageでは、センサやNodeの状態によって値を取得できない場合がある。この場合、Subscriberが値の有効性を判定できるように、messageまたはfieldについて有効性を表現する方法を定義する。

Messageの有効性と通信の成否は別の概念として扱う。MAVLink messageを正常に受信できた場合でも、そのmessageに含まれる計測値が有効であるとは限りません。

例えば、GNSS Nodeから測位情報を正常に受信した場合でも、GNSSが測位状態を確立していなければ、測位結果を有効な情報として利用できない場合があります。このような状態は、通信の成否とは別にmessageまたはfieldの状態として表現します。


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
