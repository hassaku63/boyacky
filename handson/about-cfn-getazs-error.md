# 概要

Day1 で発生した、人によって `Fn::GetAZs` と `Fn::Select` の組み合わせが期待通り動作しないケースについて調査した。

```yaml
  # 該当する記述箇所の例
  PublicSub2:
    Type: 'AWS::EC2::Subnet'
    Properties:
      CidrBlock: 10.0.0.0/24
      AvailabilityZone: !Select
        - '1'
        - !GetAZs 
          Ref: 'AWS::Region'
      VpcId: !Ref VPC
```

## 前提条件

デプロイ先のリージョンに、デフォルト VPC が存在する

## 対応方針

すべての AZ にデフォルトサブネットが作成された状態にする

## 対応手順

※ここに記述したコマンドは、 zsh で動作済み

## デフォルト VPC ID を取得

コマンド

```zsh
DEFAULT_VPC_ID=$(
    aws ec2 describe-vpcs \
    --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' --output text \
)
```

## デフォルトサブネットの確認

コマンド

```zsh
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=${DEFAULT_VPC_ID}" \
            "Name=default-for-az,Values=true" \
  --query "Subnets[*].{AvailabilityZone: AvailabilityZone,AvailabilityZoneId: AvailabilityZoneId, DefaultForAz: DefaultForAz}"
```

上記のコマンドを叩いた実行結果例は以下。

```json
[
    {
        "AvailabilityZone": "ap-northeast-1a",
        "AvailabilityZoneId": "apne1-az4",
        "DefaultForAz": true
    },
    {
        "AvailabilityZone": "ap-northeast-1c",
        "AvailabilityZoneId": "apne1-az1",
        "DefaultForAz": true
    }
]
```

ここで出てきた AZ のリストが `Fn::GetAZs` で取得できるサブネットのリストとなる。しかし、ここに含まれない AZ は `Fn::GetAZs` では取得できない。

#### Note

該当する VPC に存在するすべての AZ を確認するコマンドは以下

```zsh
aws ec2 describe-availability-zones --query "AvailabilityZones[*].ZoneName" --output text
```

## デフォルトサブネットが存在しない AZ を取得

コマンド

```zsh
DEFAULT_SUBNET_AZS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${DEFAULT_VPC_ID}" "Name=default-for-az,Values=true" --query "Subnets[*].AvailabilityZone" --output text)
ALL_AZS=$(aws ec2 describe-availability-zones --query "AvailabilityZones[*].ZoneName" --output text)

echo ${DEFAULT_SUBNET_AZS} ${ALL_AZS} | tr " \t" "\n" | sort | uniq -c | awk '{if($1 < 2) { print $2 }}'
```

実行結果例は以下

```zsh
ap-northeast-1d
```

## デフォルトサブネットを作成

先ほどのコマンドを利用して、デフォルトサブネットの追加が必要な AZ のリストを得る。

```zsh
AZS=$(echo ${DEFAULT_SUBNET_AZS} ${ALL_AZS} | tr " \t" "\n" | sort | uniq -c | awk '{if($1 < 2) { print $2 }}')
```

デフォルトサブネットを追加する。

```zsh
for az in ${AZS}; do aws ec2 create-default-subnet --availability-zone ${az} ; done
```

以上の作業を実施することで、 `Fn::GetAZs` ですべての AZ を取得できるようになる。
