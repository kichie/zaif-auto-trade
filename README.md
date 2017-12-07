# zaif-auto-trade
## 概要
zaifが公開しているAPIを使って自動でトレードをするBOTを作りました。  

1. pipコマンドを実行し、このコードに使用されているモジュールをダウンロードしてください  
`pip install zaifapi`  
`pip install pprint`  

2. zaifから取得したKEYとSECRETを下記図を参考にjson形式で置いてください  
　|- zaif_trade.py  
　|- [config] - zaifkeys.json  
　|- ...<略>

3. コードを実行してください。

__取引は自己責任です。  
このコードにより損失が出ても責任は負えません。__

## アルゴリズム
1. 前回の取引額を渡す（この金額が判断の基準となる）
2. Bitcoinを持っていて(0.001以上)かつ0.25%値上がりした場合、売る（そして、前回取引額を更新する）
3. Bitcoinを持っていない(0.001以下)かつ0.1%値下がりした場合、買う（そして、前回取引額を更新する）
4. 取引が処理されない場合、１分待って、待っても処理されない場合、キャンセルする（そして、前回取引額を元に戻す）  
5. 最後にプログラムの最初から最後までの取引にかかった時間と値段書き込む  

【参考】  
・取引後のResponseの「order_id」が0でない（order_idが発行されている）場合、取引が保留となっている。

## 参考サイト
<https://qiita.com/speedkingg/items/7f122e1fd90558c531f4#_reference-5c30a23ea79e4a9e6dc8>