from flask import make_response


def warp_resp(txt):
    rep = make_response(txt)
    rep.status_code = 200
    rep.headers["Access-Control-Allow-Origin"] = "*"
    rep.headers["Access-Control-Allow-Headers"] = "X-Requested-With,Content-Type"
    rep.headers["Access-Control-Allow-Methods"] = "POST, PUT, GET, OPTIONS, DELETE"

    return rep
