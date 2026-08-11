# Background

## Background

電装システムは、GNSS、慣性計測、対気速度計測、飛行制御、電源管理、データロギング、テレメトリおよび表示などの異なる機能を提供する複数のノードで構成される。

これらのノードは、運用中に互いにデータを交換する必要がある。さらに、電装システム内で交換されるデータの一部は、地上管制システムなどの外部システムに送信または受信される必要がある。

ノードの数と交換されるデータの種類が増えるにつれて、各ファームウェアごとに通信インターフェースを独立して定義することは維持が困難になる。そのため、ノード間のインターフェースを一貫性のあるものに保つために、共通のデータ表現と通信プロトコルが必要である。

## Communication Requirements

通信システムは以下の要件を満たす必要がある。

1. ノード間で交換されるデータは、共通かつ明確な定義を持つ必要がある。各fieldの意味、型および表現は、特定のファームウェアの実装に依存してはならない。
1. 同じmessage definitionは、複数のファームウェア実装で使用可能である必要がある。システムは異なるマイコン、プログラミング言語および開発環境を使用する可能性があり、通信インターフェースは各実装が独自のデータ表現を定義することを要求してはならない。
1. 通信データは、定義されたwire formatを持つ必要がある。フォーマットは、組み込み通信バスで使用するのに十分にコンパクトである必要があり、異なる実装間で同じ論理messageを交換できる必要がある。
1. 通信インターフェースは、code generationに適している必要がある。共通のmessage definitionは、実装固有のlibraryを生成するために使用される必要があり、serializationおよびdeserializationは各ファームウェアで独自に実装する必要がない。
1. 通信プロトコルは、オンボードのノード間だけでなく、地上管制システムやデータロガーなどの外部システムでも使用可能である必要がある。

## Protocol Selection

共通の通信インターフェースを実装するために、いくつかのアプローチがある。

1. 電装システム専用のプロトコルを定義する。このアプローチでは、message formatおよび通信動作を完全に制御できるが、独自のwire format、serializationおよびdeserializationの規則、code generation tool、および互換性の規則を定義し維持する必要がある。
1. 汎用のserializationまたはinterface-definition systemを使用する。このアプローチでは、標準化されたデータ表現およびcode generationを提供できるが、wire formatおよび通信モデルは、組み込み電装通信システムの要件に最適化されていない可能性がある。

MAVLinkは、すでに定義されたmessage model、wire format、serializationおよびdeserializationの規則、およびcode generation toolを提供しているため、このシステムの通信プロトコルとして選択された。これらの既存のメカニズムを使用することで、プロジェクトが設計および維持する必要がある通信インフラストラクチャの量を減らすことができる。

## Use of MAVLink

MAVLinkは、message definitionの表現およびwire formatを定義するだけでなく、serializationおよびdeserializationの規則も定義する。これにより、同じmessage definitionを使用して異なる実装間で同じ論理messageを交換できる。

MAVLinkには標準のmessage definitionが含まれているが、電装システムは、舵角計、風見計、対気速度計、慣性計測ユニットなどの独自のセンサーを使用するため、独自のmessage definitionが必要である。

このため、電装システムは、MAVLinkの標準のmessage definitionを使用するのではなく、独自のMAVLink dialectを定義している。

独自に定義したdialectは、電装システムで使用されるmessage definitionを含む。MAVLink 2のwire formatおよび基礎となるpacket structureは、MAVLinkによって定義されており、このプロジェクトによって再定義されることはない。

## Separation of Data Definition and Transport

通信architectureは、メッセージの定義と、そのメッセージを転送するために使用する方法を分離して開発するようにしている。

独自に定義したMAVLinkのdialectは、どの情報を交換するかを定義する。MAVLinkは、packet representationおよびserializationの規則を提供する。Transportは、特定の通信方式でのMAVLink packetを転送するための実装を提供する。

この分離により、同じmessage definitionを、基礎となる通信方式に依存せずに使用できる。例えば、電装システムは、CAN FDをSystem Busとして使用することができるが、message definition自体はCAN FDに依存しない。

結果として得られるarchitectureは、以下の責務の分離に基づいている。

```text
MAVLink Dialect
    │
    │ defines
    ▼
MAVLink Message
    │
    │ encoded according to MAVLink 2
    ▼
MAVLink Packet
    │
    │ transported by
    ▼
Transport
    │
    ▼
Communication Medium
```

## Repository Structure

通信インターフェイスは、これらの扱う範囲に応じて複数のrepositoryに分割される。

`mavlink-dialect`は、電装システムで使用されるMAVLink message definitionのsource of truthである。

`mavlink-cpp`は、ファームウェアおよびその他のC++アプリケーションで使用される生成済みのC++ libraryを提供する。このlibraryは、`mavlink-dialect`で管理されるdefinitionから生成される。

Transport固有の実装は、message definitionとは別に管理される。例えば、CAN FD Transportは`mavlink-canfd`で提供される。

よって、望ましい依存関係は以下の通りになる。

```text
mavlink-dialect
       │
       │ code generation
       ▼
mavlink-cpp
       │
       │ dependency
       ▼
Firmware / Applications
```

この構成により、各ファームウェアが独自の通信定義を維持することを防ぎ、システム全体でMAVLinkのserializationおよびTransportの実装を重複させることを避けることができる。

## Design Goals

この通信システムの設計は、以下の目標を達成することを目的としている。

1. message definitionは、単一のsource of truthとして維持される必要がある。
1. 同じmessage definitionは、異なるNodeおよびソフトウェア実装で使用可能である必要がある。
1. MAVLink固有のprotocol processingは、各ファームウェアが独自に実装するのではなく、共有の生成済みlibraryによって提供される必要がある。
1. Transport固有の動作は、個々のmessageの意味論とは独立して維持される必要がある。
1. message definition、生成済みlibraryおよびファームウェアの依存関係の変更は、version-controlled repositoryおよび自動化されたvalidationを通じて追跡可能である必要がある。

これらの目標を満たすように、このrepositoryの他のドキュメントで説明されるarchitectureおよびdevelopment processの設計を決めた。