#coding=utf-8
import logging
import json
import requests
import urllib,urllib2
from until.time import date

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y %m %d  %H:%M:%S',
                filename='log/'+ date() +'.log',
                filemode='w')

class price_and_quantity:

    def __init__(self,price,quantity):
        self.price = price
        self.quantity = quantity
        self.type = "price_and_quantity"

def log(msg):
    logging.info(msg)

class orderbook_update(object):

    def __init__(self,data):
        if data:
            self.type = "orderbook"
            self.parse_ob2(data)

    def parse_ob2(self,ob2):
        data = ob2.split("|")
        if len(data) != 10:
            return False
        self.instrument_id = data[0]
        #tmp = data[4].split(";")
        self.nbids = 0
        self.bid = []
        self.nasks = 0
        self.ask = []
        if data[2]:
            tmp = data[2].split(";")
            for update in tmp:
                atom = update.split('@')
                self.nbids += 1
                self.bid.append(price_and_quantity(atom[1],atom[0]))

        if data[3]:
            tmp = data[3].split(";")
            for update in tmp:
                atom = update.split('@')
                self.nasks += 1
                self.ask.append(price_and_quantity(atom[1],atom[0]))

class account_update(object):
    def __init__(self,data = False):
        if data:
            self.parse_account(data)

    def parse_account(self, data):
        self.account_id = data[0]['accountId'][0]
        self.balance = data[0]['balance'][0]
        self.available_funds = data[0]['availableFunds'][0]
        self.available_to_withdraw = data[0]['availableToWithdraw'][0]
        self.unrealised_profit_and_loss = data[0]['unrealisedProfitAndLoss'][0]
        self.margin = data[0]['margin'][0]
        self.active = data[0]['margin'][0]

class active_order(object):
    def __init__(self,order):
        if order:
            self.parse_input(order)

    def parse_input(self,data):
        self.type = "order"
        for tag,value in data.items():
            if tag == "timeInForce": self.time_in_force = value[0]
            elif tag == "instructionId": self.instruction_id = value[0]
            elif tag == "originalInstructionId": self.original_instruction_id = value[0]
            elif tag == "orderId":
                self.order_id = value[0]
            elif tag == "accountID":
                self.account_id = value[0]
            elif tag == "instrumentId":
                self.instrument_id = value[0]
            elif tag == "price":
                self.price = value[0]
            elif tag == "quantity":
                self.quantity = value[0]
            elif tag == "matchedQuantity":
                self.matched_quantity = value[0]
            elif tag == "cancelledQuantity":
                self.cancelled_quantity = value[0]
            elif tag == "orderType":
                self.order_type = value[0]
            elif tag == "openQuantity":
                self.open_quantity = value[0]
            elif tag == "openCost":
                self.open_cost = value[0]
            elif tag == "cumulativeCost":
                self.cumulative_cost = value[0]
            elif tag == "commission":
                self.commission = value[0]
            elif tag == "stopReferencePrice":
                self.stop_reference_price = value[0]
            elif tag == "stopLossOffset":
                self.stop_loss_offset = value[0]
            elif tag == "stopProfitOffset":
                self.stop_profit_offset = value[0]
            elif tag == "executions":
                self.executions = []
                for item in value:
                    self.executions.append(execution(item))
                #self.stop_profit_offset = value[0]

class execution(object):
    def __init__(self , data):
        execution_id = data['execution_id']
        if data.has_key("execution"):
            self.value = price_and_quantity(data['execution'][0]['price'][0] , data['execution'][0]['quantity'][0])
        else:
            self.value = price_and_quantity(0, data['orderCancelled'][0]['quantity'][0])
        self.type = data['execution']

class position(object):
    def __init__(self,data = False):
        if data:
            self.parse_input(data)

    def parse_input(self,position):
        self.type = "position"
        for tag,value in position.items():
            if tag == "accountId":
                self.account_id = value[0]
            elif tag == "instrumentId":
                self.instrument_id = value[0]
            elif tag == "valuation":
                self.valuation = value[0]
            elif tag == "shortUnfilledCost":
                self.short_unfilled_cost = value[0]
            elif tag == "longUnfilledCost":
                self.long_unfilled_cost = value[0]
            elif tag == "openQuantity":
                self.open_quantity = value[0]
            elif tag == "cumulativeCost":
                self.cumulative_cost = value[0]
            elif tag == "openCost":
                self.open_cost = value[0]


class rejected_instruction(object):
    def __init__(self,data=False):
        if data:
            self.parse_input(data)

    def parse_input(self,reject):
        self.type = "rejected_instruction"
        for tag,value in reject.items():
            if tag == "accountId":
                self.account_id = value[0]
            elif tag == "instrumentId":
                self.instrument_id = value[0]
            elif tag == "instructionId":
                self.instruction_id = value[0]
            elif tag == "reason":
                self.reason = value[0]

class lmaxapi():
    def __init__(self):
        self.connected = False
        self.http_std_headers = self.set_std_headers()
        self.account_currency = ""
        self.account_id = 0
        self.app_params = ""
        self.longpollkey = False
        self.sequence_no = False
        self.cookies = ""


    def login(self,username,password,productType = "CFD_DEMO"):
        self.username = username
        self.password = password
        self.productType = productType
        if not self.username or not self.password:
            logging.warning ("username or password is null")
            return
        if self.productType == "CFD_DEMO":
            self.url = "https://web-api.london-demo.lmax.com"
        elif self.productType == "CFD_LIVE":
            self.url = "hhttps://api.lmaxtrader.com"
        if not self.connected:
            self.connect()
        data = {"req":[{'username':self.username,'password':self.password,'productType':self.productType}]}
        logindata = json.dumps(data,False)
        res = self.post_login("/public/security/login",logindata)
        if res.status_code == 200:
            data_encode = json.loads(res.content)
            if self.check_ok(data_encode):
                logging.info("login OK")
                self.extract_login_data(data_encode)
                if self.get_app_params():
                    return True
                else:
                    return False
            else:
                logging.error("login error")

    def logout(self):
        logoutdata = "{\"req\":[{}]}"
        self.post_request("/public/security/logout",logoutdata)

    def setup_subscription(self,type = "order"):
        if self.longpollkey == False:
            self.get_longpollkey()
        if type != "order" and type != "account" and type != 'position':
            print "invalid subscription type, try one of order, account, position\n";
            return False
        postdata = "{\"req\":[{";
        postdata += "\"subscription\":[{\"type\":\""+ type +"\"}],";
        postdata += "\"longPollKey\":\""+ str(self.longpollkey) +"\"}]}"

        result = self.post_request("/secure/subscribe",postdata)

    def subscribe_to_orderbook(self,instrument_list):
        if self.longpollkey == False:
            self.get_longpollkey()

        data = "{\"req\":[{"
        for id in instrument_list:
            data += "\"subscription\":[{\"ob2\":\""+ str(id)+ "\"}],"

        data += "\"longPollKey\":\""+str(self.longpollkey)+"\"}]}"
        result = self.post_request("/secure/subscribe",data)


    def search_instruments(self,search_string = "+"):
        instruments = {}
        quit = 0
        offset = 0
        if search_string == "+":
            asset_query = "+"
        else:
            asset_query="+" + search_string;
        self.instruments = {}
        while not quit :
            result = self.get_request("/secure/instrument/searchCurrentInstruments?q=" + asset_query + "&offset=" + str(offset));
            data_encode = json.loads(result.content)
            if self.check_ok(data_encode):
                tmp = data_encode['res'][0]['body'][0]['instruments'][0]['instrument']
                for item in tmp:
                    id = str(item['id'][0].encode('utf-8'))
                    self.instruments[id] = {}
                    self.instruments[id]['id'] = item['id'][0]
                    self.instruments[id]['symbol'] = item['symbol'][0]
                    self.instruments[id]['trustedSpread'] = item['trustedSpread'][0]
                    logging.info(id+ "   "+item['symbol'][0])
            quit = 1
        #print self.instruments

    def connect(self):
        http_header =  {}
        http_header['Content-Type'] = "application/json; charset=utf-8"


    def get_events(self):
        postdata = ""
        updates = []
        if self.longpollkey == False:
            return False

        if self.sequence_no == False:
            self.sequence_no = -1

        result = self.post_request("/push/longPoll",postdata)
        if result == False:return False
        data = json.loads(result.content)

        self.sequence_no = data['events'][0]['header'][0]['seq'][0]
        for key,item in data['events'][0]['body'][0].items():

            if key == "$":
                continue
            elif key == "ob2":
                for price in item:
                    updates.append(orderbook_update(price))
                #print updates[0].bid[0].price
            elif key == "accountState":
                updates.append(account_update(item))
            elif key == "orders":
                #See RT 27031 & RT 27033 for brokenness around this call and returned data.
                if item[0]['page'][0]:
                    item = item[0]['page'][0]['order']
                    for order in item:
                        updates.append(active_order(order))

            # elif key == "order":
            #     #we normally get an array of active orders
            #     for order in item:
            #         print order
            #         updates.append(active_order(order))
            elif key == "positions":
                if item[0]['page'][0]['position']:
                    item = item[0]['page'][0]['position']

            elif key == "position":
                for value in item:
                    updates.append(position(value))
            elif key == "instructionRejected":
                for value in item:
                    updates.append(rejected_instruction(value))

        return updates

        #print  data

    def post_request(self,path,data):
        http_header = self.http_std_headers
        if self.longpollkey != False:
            http_header['longPollKey'] = self.longpollkey

        if self.sequence_no != False:
            http_header['lastReceivedMessageSequence'] = self.sequence_no
        try:
            r = requests.post(self.url + path, data=data, cookies=self.cookies , headers=http_header)
            return r
        except:
            logging.info("post_request failed")

    def post_login(self,path,data):
        http_header = self.http_std_headers
        if self.longpollkey:
            http_header['longPollKey'] = self.longpollkey;
        if self.sequence_no:
            http_header['lastReceivedMessageSequence'] = self.sequence_no;

        r = requests.post(self.url+path,data = data,headers = http_header)
        self.cookies = r.cookies
        # cookie = r.headers.get("Set-Cookie")
        # cookieArray = cookie.split(";")
        # if len(cookieArray) > 0 :
        #     self.cookies = cookieArray[0]+";"
        return r

    def get_request(self,path):

        http_header = {}
        http_header['Content-Type'] = "application/json; charset=utf-8"
        url = self.url + path
        r = requests.get(self.url+path, cookies=self.cookies ,headers = http_header)
        return r


    def check_ok(self, data):
        if not data:
            return False
        res_status = data['res'][0]['header'][0]['status'][0].encode('utf-8')
        if res_status != "OK":
            return False
        return True

    def extract_login_data(self,data):
        self.account_id = data['res'][0]['body'][0]['accountId'][0].encode('utf-8')
        self.account_currency = data['res'][0]['body'][0]['currency'][0].encode('utf-8')

    def get_app_params(self):
        if not self.app_params:
            r = self.get_request("/secure/getApplicationParameters")
            data_encode = json.loads(r.content)
            if r.status_code == 200 and self.check_ok(data_encode):
                tmp = data_encode['res'][0]['body']
                logging.info(tmp)
                return True
            else:
                return  False


    def set_std_headers(self):
        headers = {}
        headers['Host'] = "web-api.london-demo.lmax.com"
        headers['User-Agent'] = "LMAX Python client"
        headers['Content-Type'] = "application/json; charset=utf-8"
        headers['Accept'] = "application/json"
        headers['Keep-Alive'] = "115"
        headers['Connection'] = "keep-alive"
        headers['Accept-Language'] = "en-gb,en;q=0.5"
        headers['Accept-Charset'] = "ISO-8859-1,utf-8;q=0.7,*;q=0.7"
        return headers

    def get_longpollkey(self):
        result = self.get_request("/secure/longPollKey")
        data_encode = json.loads(result.content)
        if not self.check_ok(data_encode):
            return False

        tmp = data_encode['res'][0]['body'][0]
        self.longpollkey = tmp['longPollKey'][0]
        return self.longpollkey

    def close_order(self,instrument_id=False, order_id=False, quantity = 0):
        if instrument_id and order_id and quantity!=0:
            data = "{\"req\":[{"
            data += "\"instrumentId\":\""+ str(instrument_id)+"\""
            data += ",\"originalInstructionId\":\""+str(order_id)+"\""
            data += ",\"quantity\":\""+ str(quantity)+"\""
            data += "}]}"
            result = self.post_request("/secure/trade/closeOutOrder", data)
            data_encode = json.loads(result.content)
            if not self.check_ok(data_encode):
                logging.info("LMAXAPI: request rejected")
                return False

            return_id = data_encode['res'][0]['body'][0]['instructionId'][0]
            return return_id



    def place_order(self,instrument_id,ordertype,fill_type,quantity,price=False,order_id=False,stop_price=False):
        if self.longpollkey == False:
            self.get_longpollkey()

        good_until = ""
        partial_match = ""
        timeinforce = "ImmediateOrCancel"
        is_stop = False
        sanity = False

        if ordertype == order_type.market:
            if fill_type == fill_strategy.IoC or fill_type == fill_strategy.FoK:
                sanity = True
        elif ordertype == order_type.limit:
            if fill_type == fill_strategy.IoC or fill_type == fill_strategy.FoK or fill_strategy.GTC or fill_type == fill_strategy.GFD:
                sanity = True
        elif ordertype == order_type.market_stop:
            if fill_type == fill_strategy.GFD:
                sanity = True
        if not sanity:
            logging.info("LMAXAPI: failed sanity test for order type and fill strategy")
            return False

        if ordertype == order_type.limit and price == False:
            logging.info("LMAXAPI: need a price for a limit order")
            return False

        if ordertype == order_type.market_stop and stop_price == False:
            logging.info("LMAXAPI: need a stop price for a market stop order")
            return False

        if fill_type == fill_strategy.fill_or_kill:
            timeinforce = "FillOrKill"
        elif fill_type == fill_strategy.immediate_or_cancel:
            timeinforce = "ImmediateOrCancel"
        elif fill_type == fill_strategy.good_for_day:
            timeinforce = "GoodForDay"
        elif fill_type == fill_strategy.good_til_cancel:
            timeinforce = "GoodTilCancelled"
        else:
            logging.info("LMAXAPI: unknown fill_strategy")
            return False
        data = "{\"req\":[{\"order\":[{"
        data += "\"instrumentId\":\""+ str(instrument_id)+"\",\"quantity\":\""+str(quantity)+"\",\"timeInForce\":\""+timeinforce+"\","
        if order_type == order_type.limit:
            data += "\"price\":\""+price+"\","

        if order_type == order_type.market_stop:
            data += "\"stopCondition\":[{\"price\":\""+stop_price+"\"}],"
        data += "}]}]}"

        result = self.post_request("/secure/trade/placeOrder",data)
        data_encode = json.loads(result.content)
        if not self.check_ok(data_encode):
            logging.info("LMAXAPI: request rejected")
            return False
        return_id = data_encode['res'][0]['body'][0]['instructionId'][0]
        return return_id


class order_type():
    market = 0
    limit = 1
    market_stop = 2

class fill_strategy():
    fill_or_kill = 0
    immediate_or_cancel = 1
    good_for_day = 2
    good_til_cancel = 3
    FoK = 0
    IoC = 1
    GFD = 2
    GTC = 3





















