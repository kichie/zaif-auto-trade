
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 23:10:53 2017

@author: kichie
"""

import json
import time
import pprint
from zaifapi import ZaifPublicApi
from zaifapi import ZaifTradeApi
from decimal import (Decimal)

zaif_keys_json = open('config/zaifkeys.json', 'r')
zaif_keys = json.load(zaif_keys_json)

KEY = zaif_keys["key"]
SECRET = zaif_keys["secret"]
not_able_bid_count = 0
count=0
interval = 1
trade_result = {"order_id" : 0}
#last_trade_priceよりも上がりすぎて戻ってこない場合再取得
def resetlast_trade_price(zaif_public,last_trade_price,funds_btc):
    global not_able_bid_count
    
    if(funds_btc < 0.001 and not_able_bid_count >= 3):
        last_trade_price = int(zaif_public.last_price('btc_jpy')["last_price"])
        print("recount"+str(not_able_bid_count))
        not_able_bid_count=0
    elif(funds_btc < 0.001):
        not_able_bid_count += 1
    
    
def writingData():
    
    global elpsed_time,last_trade_price
    #取引時間の書き込み
    time_f = open("tradingTime",'a')
    time_f.write(str(elpsed_time)+"\n")
    time_f.close()
    
    last_price_f = open("tradingPrice",'a')
    last_price_f.write(str(last_trade_price)+"\n")
    last_price_f.close()


if __name__=='__main__':
    # get environ ver
    zaif_public = ZaifPublicApi()
    zaif_trade = ZaifTradeApi(KEY,SECRET)
    
    CANCEL_FLUG = False
    
    last_trade_price = int(zaif_public.last_price('btc_jpy')["last_price"])
    
    
    while(True):
        start_time = time.time()
        print("■ 現在の情報です")
        try:
            funds_btc = zaif_trade.get_info2()['funds']['btc']
            funds_jpy = zaif_trade.get_info2()['funds']['jpy']
            last_price = int(zaif_public.last_price('btc_jpy')["last_price"])
            
        except:
            print("Error:Can't get data")
        finally:
            print("市場取引価格:"+str(last_price))
            print("btc資産:"+str(funds_btc))
            print("jpy資産:"+str(funds_jpy))
            print("最終取引価格:"+str(last_trade_price))
        
        
        #btcを持っていて0.25%値上がり
        if(funds_btc >= 0.001 and int(last_trade_price*1.0025)< last_price):
            #売却
            ask_amount = Decimal(funds_btc).quantize(Decimal('0.0001'))
            try:
                trade_result = zaif_trade.trade(currency_pair="btc_jpy", action="ask", price=last_price, amount=ask_amount)
                last_trade_price_pre = last_trade_price
                last_trade_price = last_price
                
                print('■ Bitcoinの売却申請を行いました。')
                pprint.pprint(trade_result)
                print("売却注文価格:"+str(last_price))
                print("売却注文量　:"+str(ask_amount))
            except:
                print("Error:cant trade[ask_up]")
            
            if(trade_result["order_id"] != 0):
                CANCEL_FLUG = True
                order_id = trade_result["order_id"]
            else:
                print("■ 取引が完了しました。")
        #btcを持っていて0.1%値下がり
        elif(funds_btc >= 0.001 and int(last_trade_price*0.999) > last_price):
            try:
                #売却
                ask_amount = Decimal(funds_btc).quantize(Decimal('0.0001'))
                trade_result = zaif_trade.trade(currency_pair="btc_jpy", action="ask", price=last_price, amount=ask_amount)
                last_trade_price_pre = last_trade_price
                last_trade_price = last_price
                print('■ Bitcoinの売却申請を行いました。')
                pprint.pprint(trade_result)
                print("売却注文価格:"+str(last_price))
                print("売却注文量　:"+str(ask_amount))
            except:
                print("Error:Can't trade[ask]")
                
            if(trade_result["order_id"] != 0):
                CANCEL_FLUG = True
                order_id = trade_result["order_id"]
            else:
                print("■ 取引が完了しました。")
        #btcを持っていないでlastpriceより値下がりしたら買い
        elif(funds_btc < 0.001 and last_price < last_trade_price):
            try:
                bid_amount = 0.0001
#                bid_amount = (Decimal(funds_jpy)/last_price).quantize(Decimal('0.0001'))
                trade_result = zaif_trade.trade(currency_pair="btc_jpy", action="bid", price=last_price, amount=bid_amount)
                last_trade_price_pre = last_trade_price
                last_trade_price = last_price
                not_able_bid_count = 0
                print('■ Bitcoinの購入申請を行いました')
                pprint.pprint(trade_result)
                print("購入注文価格:"+str(last_price))
                print("購入注文量　:"+str(bid_amount))
            except:
                print("Error:Can't trade[bid]")
                
            if trade_result["order_id"] != 0:
                CANCEL_FLUG = True
                order_id = trade_result["order_id"]
            else:
                print('■ 取引が完了しました。')
            
            if CANCEL_FLUG:
                try:
                    trade_info = zaif_trade.get_info2()
                    if trade_info["open_orders"] > 0:
                        print("■ キャンセルしました")
                        print(zaif_trade.cancel_order(order_id=order_id))
                        last_trade_price = last_trade_price_pre
                    else:
                        print("■ 取引が完了しました。")
                except:
                    print("Error:Can't trade[cancel]")
        
        resetlast_trade_price(zaif_public,last_trade_price,funds_btc)
        
        end_time = time.time()
        elpsed_time = end_time-start_time
        if elpsed_time > 30:
            elpsed_time %= 30
            print("take time over 30sec")
        
        print(elpsed_time)
        
        #取引時間の書き込み
        writingData()
        
        
        time.sleep(30-elpsed_time)
        
        
        count+=1
        print(not_able_bid_count)
        print(count)
