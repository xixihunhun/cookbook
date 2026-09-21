from flask import jsonify

def success(data=None, msg="ok"):
    return jsonify({
        "code": 200,
        "msg": msg,
        "data": data
    })

def fail(code=400, msg="参数错误"):
    return jsonify({
        "code": code,
        "msg": msg
    }), code