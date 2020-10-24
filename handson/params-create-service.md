# params-create-service

Docs:

Docs: 

- [AWS CLI - aws.ecs.create-service](https://docs.aws.amazon.com/cli/latest/reference/ecs/create-service.html)
- [AWS Developer guide - Amazon ECS services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)

### ecs create-service パラメータ仕様

param | description
---|---
[--cluster \<value\>] |  ECS クラスタの名前
--service-name \<value\> | デプロイするサービスの名前
[--task-definition \<value\>] | 基になるタスク定義の名前
[--load-balancers \<value\>] |  このサービスに利用するロードバランサの設定。Load Balancer object のリスト (後述)
[--service-registries \<value\>] | このサービスに割り当てる Service Discovery (今回は不使用)
[--desired-count \<value\>] | 常時稼働していて欲しいタスクの数
[--client-token \<value\>] | -
[--launch-type \<value\>] | サービスの起動タイプ (EC2/FARGATE). `--capacity-provider-strategy` とは排他の関係
[--capacity-provider-strategy \<value\>] | タスクの実行基盤となる [Capacity Provider](https://docs.aws.amazon.com/cli/latest/reference/ecs/create-capacity-provider.html) をどのように選択するか、その重み付けの配分を指定。 `--launch-type` とは排他的関係
[--platform-version \<value\>] | (Fargate のみ) Fargate プラットフォームのバージョン指定。デフォルトは `LATEST` (参考: [AWS Fargate platform versions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html))
[--role \<value\>] | ECS サービスがロードバランサを呼び出すための IAM ロール。サービスにロードバランサを割り当てる場合、かつ `awsvpc` ネットワークモード**不使用**の場合（よって Fargate 起動タイプでは非該当）のみ、指定してよい
[--deployment-configuration \<value\>] | デプロイの間、どれだけのタスクを走らせておきたいかのポリシー設定。 `--desired-count` に対する最小／最大の**割合**を指定
[--placement-constraints \<value\>] | 開始するサービス／タスクをどの基盤に配置するかの制約を追加する。例えば「同種のタスクは必ず異なるコンテナインスタンスに配置する」ように指定することが可能。<br/>参考: [Amazon ECS task placement constraints](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-placement-constraints.html)
[--placement-strategy \<value\>] | サービス／タスクを配置する先をどのようにして決定するか、指定する。例えば、既に起動中のコンテナインスタンスのリソースの未使用を最大限なくすようにしたり、コンテナインスタンスあるいは AZ でできるだけ均等になるような配置戦略を指示できる。<br>[Amazon ECS task placement strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-placement-strategies.html)
[--network-configuration \<value\>] | デプロイする VPC/Subnet や SecurityGroup に関する設定
[--health-check-grace-period-seconds \<value\>] | タスクが開始してから、指定秒数だけ ELB Target Health Check の結果を無視する。タスクの起動に時間がかかることがわかっている場合に意図しない Unhealthy を防止するために指定
[--scheduling-strategy \<value\>] | 起動中のタスク数を維持するためのスケジューラサービスに、どのようにタスクを維持するかのポリシーを指定する。REPLICA/DAEMON がサポートされており、**Fargate では REPLICA のみ対応**。<br/>参考: [Amazon ECS services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)
[--deployment-controller \<value\>] | サービスにどのデプロイ戦略を適用するかを指定する。 ECS/CODE_DEPLOY/EXTERNAL が指定可能。
[--tags \<value\>] | -
[--enable-ecs-managed-tags \| --no-enable-ecs-managed-tags] | Enable にした場合は、サービス／タスクに対して ECS が自動でタグを割り当てる。サービスに対してはクラスタ名を、タスクに対してはクラスタ名とサービス名のタグを付与する。<br/>参考: [Tagging your Amazon ECS resources](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-using-tags.html) ... "Tagging your resources for billing" を参照
[--propagate-tags \<value\>] | 実行されるタスクに対して、タスク定義のタグもしくはサービスのタグを継承したい場合に指定。 TASK_DEFINITION/SERVICE いずれかを指定可能。
[--cli-input-json \<value\>] | -
[--generate-cli-skeleton \<value\>] | -

ローンチするネットワークの設定 `--network-configuration` がサービス作成の引数として初めて出てきたことに着目してください。
**タスク定義では「どのようなコンテナが立ち上がってくるのか」といったコンテナ自身のことに主な関心**がありました。対して、サービスの関心事は **「どこで、どのようにデプロイするのか」**であることが上記のパラメータシートからもわかると思います。

#### --load-balancers

サービスをフェイシングする ELB に関する設定です。

オブジェクトのリスト形式で表現します。1つのオブジェクトは次のフォーマットを持つ json です。

```json
{
    "targetGroupArn": "<string>",
    "loadBalancerName": "<string>",
    "containerName": "<string>",
    "containerPort": "<integer>"
}
```

`--deployment-controller` などの指定値や、起動タイプ、ネットワークモードなどによって必要な設定は異なります。CLI のドキュメントから抜粋して紹介します。

- `--deployment-controller="ECS"` かつ ALB or NLB を使用している場合は複数のターゲットグループを指定可能
- `--deployment-controller="CODE_DEPLOY"` である場合
  - CLB はサポートされず ALB, NLB のどちらかを指定する必要がある
  - 2つのターゲットグループを指定する（Blue系/Green系 の切り替えを CodeDeploy が制御するために、2つのターゲットグループを利用している）
- `--deployment-controller="ECS"` の場合、ターゲットの設定情報 (Load Balancer/Target Group/Container/Port) は変更不可能 (指定を間違えた場合はサービスを作り直す必要がある)
- ALB, NLB を使用する場合は、必ず "TargetGroupArn", "Container", "ContainerPort" を指定している必要がある
  - コンテナの名前は、タスク定義の中で "ContainerDefinition" として指定した名前
  - 新しいサービスが配置されたとき、この設定内容に基づいて ALB/NLB ターゲットグループに対してターゲットを自動登録する
- CLB を利用する場合は "LoadBalancer", "ContainerPort" を指定する必要がある
- `awsvpc` ネットワークモードを使用している場合
  - ALB, NLB のみがサポートされている（よって、 Fargate サービスのフェイシングに ELB は使用できない）
  - "TargetGroup" を指定している場合、ターゲットタイプは "ip" でなければならない（"instance" は使用不可能）

#### --deployment-configuration

デプロイ中のタスク数を制御するためのパラメータです。

以下の構造を持ちます。

```json
{
    "maximumPercent": "<integer>",
    "minimumHealthyPercent": "<integer>"
}
```

`--deployment-contoroller` の設定値によってパラメータの解釈が異なります。ローリングデプロイ (`--deployment-contoroller="ECS"`) の場合を抜粋して紹介します。

- maximumPercent
  - RUNNING or PENDING 状態のタスクの最大値。デフォルトは 200%
  - `--desired-count` に対して maximumPercent を掛けて、少数以下を**切り捨て**した数が実質的なタスク数
  - ECS のサービススケジューラに対して、このパラメータでデプロイのバッチサイズを指示できる
    - 例) desired=4, maximumPercent=200 の場合
      - ECS サービススケジューラはデプロイ時に（旧タスクを停止させる前に）新しいタスクを4つデプロイすることがある（クラスタの余剰リソースが足りている場合）
- minimumHealthyPercent
  - デプロイ中に維持したい、 RUNNING 状態にあるタスク数の最小値。デフォルトは 100%
  - `--desired-count` に対して maximumPercent を掛けて、少数以下を**切り上げ**した数が実質的なタスク数
  - クラスタのキャパシティを追加せずに、デプロイできる可能性がある
    - 例) desired=4, minimumHealthyPercent=50 の場合
      - ECS スケジューラは新しいタスクを起動する前に2つのタスクを終了させ、クラスタのキャパシティを解放することがある

これらの定義の理解には、タスクのライフサイクルへの理解も必要です。公式ドキュメント [Task lifecycle](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-lifecycle.html) も参考にしてみてください。

#### --network-configuration

デプロイ先の VPC やタスクに割り当てる SG に関する設定を行います。

このパラメータは以下のような構造を持つ json オブジェクトです。

```json
{
  "awsvpcConfiguration": {
    "subnets": ["string", ...],
    "securityGroups": ["string", ...],
    "assignPublicIp": "ENABLED"|"DISABLED"
  }
}
```

サブネットは上限16個まで指定可能、SG は上限5個まで指定可能です。また、サブネットと SG は同じ VPC のリソースである必要があります。

#### --deployment-controller

"ECS" はローリングデプロイをサポートします。 `--deployment-configuration` で指定した min/max の割合に基づいて、 Healthy 状態のタスク数がその範囲に維持されるように ECS がタスクのリプレースを制御します。

"CODE_DEPLOY" では blue/green デプロイをサポートし、 "EXTERNAL" はそれ以外のデプロイ戦略を適用したい場合に指定します。これらは今回は解説できないので割愛