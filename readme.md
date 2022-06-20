## md_validatorについて

md_validatorはCSVフォーマットのマスターデータに対してバリデータを実行します。  
バリデータは簡易なコマンドの組み合わせで作ることが可能です。  
バリデータは検証の対象になるデータを絞り込むためのfilterコマンドと、検証処理本体のvalidationコマンドからなります。  
どちらのコマンドもpythonスクリプトで自作することが可能です。

## このツールの目的

* 案件毎に個別のバリデータシステムを作りたくない
* バリデーションの拡張性
* プランナーでもバリデータを書けること
    * 運用していく中でプランナーしか知らないルールができる事もある。そのルールに合ったバリデーションをプランナー自身が作成できるようにするため。
* 学習コストはなるべく低く
    * 難しいものは使われない

## 開発環境

Python 3.8.2

## 使い方

1. `master_data`フォルダにマスターデータのcsvファイルを入れる
2. `master_validator/validator`フォルダにマスタに対応するバリデータを書いたテキストファイルを保存する
3. `cd master_validator`
4. main.pyを実行する

バリデーションエラーがあれば以下のように表示されます。

```text
INFO:root:master=<item_sample> validation=<count_validation> error_message=<3件以上のレコードがありません。2件> error_master_data=<[]>
INFO:root:master=<character_sample> validation=<time_0sec_validation> error_message=<start_dataの秒が0秒になっていません。> error_master_data=<[MasterRow(row={'id': '1', 'name': 'キャラ1', 'attack': '1', 'defence': '11', 'start_data': '2022-05-01 13:59:59'}), MasterRow(row={'id': '6', 'name': 'キャラ6', 'attack': '6', 'defence': '10', 'start_data': '2022-05-05 14:59:59'})]>
```

## 対応フォーマット

`id`カラムが存在するCSVにのみ対応しています。  
CSVを使うことにしたのはpythonだけで実行できるからと、よくソシャゲ開発で使われているフォーマットだからです。
CSVから読み込むことでDBなどの他の環境を作らなくてもよくなります。

## バリデーターファイルの書き方

バリデーターを記載するためのバリデーターファイルは `validator` フォルダ内に作成します。  
`master_data` フォルダ内のcsvファイルと同名のバリデーターファイルがそのマスターデータのバリデータになります。  
バリデーターは、 `フィルターコマンド(引数) > バリデーションコマンド(引数)` のように書きます。  
複数のフィルターを連続で繋げる場合は `フィルターコマンド(引数) > フィルターコマンド(引数) > バリデーションコマンド(引数)` のように書きます。

バリデーターファイルのルールは以下です。

* master_dataフォルダ内のcsvとvalidatorフォルダ内のバリデーターファイルは同名にする
* 一つのバリデーターファイル内に複数のバリデーションを設定できる。複数ある場合は改行する
* 一つのバリデーションの最後のコマンドは必ずvalidationコマンドにする。validationコマンドは1行につき一つだけにする

## フィルター、バリデーションコマンドの拡張

フィルター、バリデーションコマンドは自作することができます。  
作り方のルールは以下です。

* `master_validator/command` フォルダにコマンドの処理をコーディングしたpythonスクリプトを保存する
* ファイル名と関数名は同じ名前にする。filterコマンドの場合は末尾を `filter` に、validationコマンドの場合は末尾を `validation` にする
* 名前はスネークケース
* 引数について
    * filterコマンドの第1引数は自動で渡されるので必須となる。 `master_data: MasterDataManipulator` のようにMasterDataManipulatorクラスにする
    * validationコマンドの引数もfilterコマンドと同様
    * 第2引数以降は任意。型は文字列型になる
* 戻り値について
    * filterコマンドは引数で渡された `MasterDataManipulator` クラスのインスタンスを返す。
    * validationコマンドは `ValidationResult` 抽象基底クラスを継承した具象クラスのインスタンスを返す。現在、具象クラスは `RowsResult`を用意しているのでこれを使う。
* 関数の処理内容
    * filter関数は、 `MasterDataManipulator` の属性である `self._rows` にマスタデータが入っているのでこれを操作して対象となるマスターデータを絞り込んでいく
    * validation関数は、受け取った `MasterDataManipulator` インスタンスのマスターデータを検証する処理を書く。エラー情報を `RowsResult` に詰めて返す。
