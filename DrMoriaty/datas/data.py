from qlib.data import dbobj, Cache
from qlib.data import GotRedis
from DrMoriaty.setting import DB_FOFA
import contextlib
from base64 import b64decode, b64encode
import json


@contextlib.contextmanager
def use_db():
    try:
        ca = Cache(DB_FOFA)
        yield ca

    finally:
        del ca

def get_db():
    return Cache(DB_FOFA)


@contextlib.contextmanager
def use_mem_db():
    try:
        ca = Cache("/tmp/memory.db")
        yield ca
    finally:
        del ca

class Info(dbobj):pass

class Host(dbobj):pass

class Checken(dbobj):pass
# Info(title=ti,ip=ip,ports=ports,os=os,ctime=time,geo=geo,body=body)

class RequestDB(dbobj):

    def to_header(self):
        return json.loads(self.headers)

    def to_text(self):
        req_header_text = "%s %s %s\n%s" % (self.command, self.path, self.request_version, self.to_header())
        return req_header_text


class BPData:

    @staticmethod
    def save_req_res(req, req_body, res, res_body):
        req_data = "%s %s %s\r\n%s" % (req.command, req.path, req.request_version, req.headers)
        if req_body:
            req_data += "\r\n\r\n%s" % req_body.decode()
            #     req_header_text = "%s %s %s\n%s" % (req.command, req.path, req.request_version, req.headers)
        res_data = "%s %d %s\r\n%s" % (res.response_version, res.status, res.reason, res.headers)
        if res_body:
            content_type = res.headers.get('Content-Type', '')
            encoding = content_type.split("charset=")
            if len(encoding) ==2:
                encoding = encoding[1]
            else:
                encoding = 'utf-8'
            res_data += "\r\n\r\n%s" % res_body.decode(encoding, 'ignore')
        print(req_data)
        redis = GotRedis()
        l = len(redis.redis.hkeys('req'))
        redis.redis.hset('req', l, req_data)
        redis.redis.hset('res', l, res_data)

    @staticmethod
    def get_data(num):
        return GotRedis().redis.hget('req', num)

    @staticmethod
    def add_target(host):
        redis = GotRedis()
        l = len(redis.redis.hkeys('hosts'))
        redis.redis.hset('hosts', l, host)

    @staticmethod
    def if_in_hosts(host):
        if host in BPData.get_hosts():
            return True
        return False

    @staticmethod
    def clear():
        redis = GotRedis()
        redis.redis.delete("hosts")
        redis.redis.delete("req")
        redis.redis.delete("res")


    @staticmethod
    def get_hosts():
        redis = GotRedis()
        return [i.decode() for i in redis.redis.hvals('hosts')]

    @staticmethod
    def get_all_req():
        redis = GotRedis()
        return [i[1] for i in sorted(redis.redis.hgetall("req").items(), key=lambda x: int(x[0]))]



    @staticmethod
    def get_all_res():
        redis = GotRedis()
        return [i[1] for i in sorted(redis.redis.hgetall("res").items(), key=lambda x: int(x[0]))]
    # def get_req_res()

    # def save_res(res, res_body)

class ResponseDB(dbobj):

    def to_header(self):
        return json.loads(self.headers)

    def to_text(self):
        
        res_header_text = "%s %d %s\n%s" % (self.response_version, self.status, self.reason, self.to_header())
        return res_header_text


def saveResponse(req_id,res, res_body):
    res_body_text = ""
    if res_body is not None:
        
        content_type = res.headers.get('Content-Type', '')

        if content_type.startswith('application/json'):
            try:
                json_obj = json.loads(res_body)
                json_str = json.dumps(json_obj, indent=2)
                if json_str.count('\n') < 50:
                    res_body_text = json_str
                else:
                    lines = json_str.splitlines()
                    res_body_text = "%s\n(%d lines)" % ('\n'.join(lines[:50]), len(lines))
            except ValueError:
                res_body_text = res_body
        elif content_type.startswith('text/html'):
            m = re.search(r'<title[^>]*>\s*([^<]+?)\s*</title>', res_body, re.I)
            if m:
                h = HTMLParser()
                
        elif content_type.startswith('text/') and len(res_body) < 1024:
            res_body_text = res_body

    res_data = ResponseDB(req_id=req_id ,response_version=res.response_version, status=res.status ,reason=res.reason, headers=json.dumps(req.headers), res_body=res_body_text)
    return res_data


def saveRequest(req_id, req, req_body):
    req_body_text = ""
    content_type = req.headers.get('Content-Type', '')
    if content_type.startswith('application/x-www-form-urlencoded'):
        req_body_text = parse_qsl(req_body)
    elif content_type.startswith('application/json'):
        try:
            json_obj = json.loads(req_body)
            json_str = json.dumps(json_obj, indent=2)
            if json_str.count('\n') < 50:
                req_body_text = json_str
            else:
                lines = json_str.splitlines()
                req_body_text = "%s\n(%d lines)" % ('\n'.join(lines[:50]), len(lines))
        except ValueError:
            req_body_text = req_body
    elif req_body and len(req_body) < 1024:
        if req_body:
            req_body_text = req_body

    if req_body_text:
        req_body_text = req_body_text
    else:
        req_body_text = req_body
    
    req_data = RequestDB(req_id=req_id, host=req.headers.get('Host','Unknow'),command=req.command, path=req.path, request_version=req.request_version, headers=json.dumps(req.headers), req_body=req_body_text)
    return req_data
