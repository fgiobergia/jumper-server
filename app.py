import json
import os
from flask import Flask, request, jsonify
from peaks import find_skips

app = Flask(__name__)
api_version = 2
auth_key = "abc123"
outdir = "storage"

tmp_storage = {}
tmp_count = 0

@app.route(f"/api/v{api_version}/<user_id>/new", methods=["GET"])
def new_session(user_id):
    pass

@app.route(f"/api/v{api_version}/<session_id>/close", methods=["GET"])
def close_session(session_id):
    pass

@app.route(f"/api/v{api_version}/<session_id>/store", methods=["POST"])
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
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
