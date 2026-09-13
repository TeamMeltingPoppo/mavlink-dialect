
## Definition of Term

本章では、本仕様で使用する主要な用語について説明します。

### MAVLink

システム間で構造化されたデータを交換するための軽量なメッセージングプロトコルです。本システムでは、電装システム間および電装システムと地上システムとの間でデータを交換するためにMAVLinkを使用します。

### MAVLink dialect

MAVLinkで交換するメッセージ、列挙型、コマンドなどのデータ定義をまとめたものです。本repositoryでは、本システムで使用するMAVLink dialectを定義します。

### MAVLink message

MAVLink dialectによって定義される論理的なデータ単位です。MAVLink messageは、複数のfieldから構成され、各fieldはデータ型、意味および単位を持ちます。

### Field

MAVLink messageを構成する個々のデータ要素です。Fieldには、名前、データ型および意味が定義されます。必要に応じて、単位、スケールなども定義されます。

### Wire format

通信媒体上でデータを交換するために使用するバイト列の構造および符号化規則です。Wire formatは、論理的なデータの表現方法と、通信上で実際に扱われるバイト列との対応を規定します。本システムでは、MAVLink 2がMAVLink messageをMAVLink packetとして表現するwire formatを規定します。

### MAVLink packet

MAVLinkのwire formatに従ってMAVLink messageを符号化したバイト列です。MAVLink packetには、messageの識別情報、payloadおよび整合性を確認するための情報などが含まれます。

### Transport

MAVLink packetをある通信ノードから別の通信ノードへ転送するための仕組みです。本システムでは、CAN FDなどの通信方式をMAVLink packetのtransportとして使用します。

### Transport frame

transportが通信媒体上で転送するデータ単位です。例えばCAN FDをtransportとして使用する場合、CAN FD frameがtransport frameに相当します。MAVLink packetとtransport frameは異なる概念であり、1つのMAVLink packetを複数のtransport frameに分割して転送する場合があります。

### Node

MAVLink messageを送信または受信するシステム上の通信主体です。Nodeには、例えばGNSS基板、IMU基板、フライトコンピュータ、データロガーおよびGround Control Systemが含まれます。