import json
import datetime
import os
import sqlite3
from flask import Flask, request, jsonify
from peaks import find_skips
import secrets

tmp_storage = {}
tmp_count = 0

def create_app(user_config):
    default_config = {
        "outdir": "storage",
        "database_path": "storage.db",
        "session_timeout": 3600*2, # 2 hours sessions
    }

    config = { **default_config, **user_config }

    app = Flask(__name__)
    
    def get_db():
        return sqlite3.connect(config["database_path"])
    
    @app.route("/sessions/<user_id>/new", methods=["GET"])
    def new_session(user_id):
        """
        (a) If `user_id` does not exist, return 401 unauthorized

        (b) If a valid session already exists for `user_id`, return that session id

        (c) Otherwise, return a new session id
        """
        con = get_db()
        cur = con.cursor()

        res = cur.execute("select count(*) from users where id = ?", (user_id,))
        count, = res.fetchone()
        if count == 0: # (a)
            return jsonify({ "status": "unauthorized", "message": "no user found"}), 401 # no user found
        
        res = cur.execute("select id from sessions where user_id = ? and creation > ?", (user_id, datetime.datetime.now() - datetime.timedelta(seconds=config["session_timeout"]),))

        sess_id = res.fetchone()

        if sess_id: # (b)
            return jsonify({"status": "OK", "session_id": sess_id[0]})
        
        else: # (c)
            # create new session
            sess_id = secrets.token_hex()
            # TODO: check whether the session id already exists!
            # unlikely, though -- it's a 256 bit key!

            cur.execute("insert into sessions (user_id, id, creation) values (?, ?, ?)", (user_id, sess_id, datetime.datetime.now()))
            con.commit()

            return jsonify({"status": "OK", "session_id": sess_id})

        pass

    @app.route("/sessions/<session_id>/close", methods=["GET"])
    def close_session(session_id):
        pass
    
    return app
"""
    @app.route("/sessions/<session_id>/store", methods=["POST"])
    def reading(session_id):
        pass

        global tmp_storage, tmp_count
        obj = request.json
        auth_key_submitted = obj.pop("authKey")
        seq = obj.pop("payload")
        if auth_key_submitted != auth_key:
            return jsonify({"status": "unauthorized"}), 401

        tmp_storage.update(seq)

        # immediately count the number of steps in this chunk sent by the client
        skips_count = find_skips(seq)
        # also, keep "tmp_count" updated with the number of skips that we have
        # currently (i.e. since the latest storage) sent the client
        tmp_count += skips_count

        print(len(tmp_storage)) # debug message (TODO: use logging)

        if len(tmp_storage) > 500:
            min_ts = min(tmp_storage.keys())

            # now count the "correct" number of skips (i.e. on the entire "tmp_storage" buffer
            # The result is then compared with "tmp_count" (the count that has been sent thus far)
            # Only the delta is sent (to provide the correct count to the client)
            skips_count = find_skips(tmp_storage) # "true" count

            # now skips_count contains the "adjusting" value (i.e. the offset from what we
            # previously told the client to the "correct" number. We send this offset so
            # that the client has a valid estimate (can be positive or negative)
            skips_count = skips_count - tmp_count 

            with open(os.path.join(outdir, f"{min_ts}.json"), "w") as f:
                json.dump(tmp_storage, f)
                tmp_storage = {}
                tmp_count = 0 # reset count

        return jsonify({"status": "OK", "count": skips_count }), 200
"""

if __name__ == "__main__":
    config = {
        "outdir": "storage",
        "database_path": "storage.db",
    }

    create_app(config).run(debug=True, host="0.0.0.0")