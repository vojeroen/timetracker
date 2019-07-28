import datetime
import json
from collections import namedtuple

import pandas as pd
import pytz
import requests
from flask import Flask, render_template, request
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../data/timetracker.db"

api = Api(app)
db = SQLAlchemy(app)


def ts_to_unix(ts):
    return int((ts.astimezone(pytz.utc) - pytz.utc.localize(datetime.datetime(1970, 1, 1))).total_seconds())


def unix_to_ts(ts):
    return pytz.utc.localize(datetime.datetime.utcfromtimestamp(ts))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "order": self.order,
            "name": self.name
        }


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("action.id"), nullable=False)
    timestamp_start = db.Column(db.Integer, nullable=False)
    timestamp_end = db.Column(db.Integer, nullable=True)
    elapsed = db.Column(db.Integer, nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_id": self.action_id,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": self.timestamp_end,
            "elapsed": self.elapsed,
        }


@app.route('/')
def main():
    return render_template("main.html")


class ResourceUserList(Resource):
    def post(self):
        data = request.json
        user = User(name=data["name"])
        db.session.add(user)
        db.session.commit()
        return user.serialize()


class ResourceAction(Resource):
    def get(self):
        return [action.serialize() for action in db.session.query(Action).all()]

    def post(self):
        data = request.json
        order = db.session.query(func.max(Action.order)).one()[0]
        if order is None:
            order = 0
        action = Action(name=data["name"],
                        order=order + 1)
        db.session.add(action)
        db.session.commit()
        return action.serialize()

    # def put(self):
    #     data = request.data
    #     action = db.session.query(Action).filter(Action.id == data["id"]).one()
    #     action.name = data["name"]
    #     db.session.commit()
    #     return action.serialize()


class ResourceRegistration(Resource):
    def get(self):
        user_id = db.session.query(User).one().id
        latest = request.args.get("latest", False)

        registrations = db.session \
            .query(Registration) \
            .filter(Registration.user_id == user_id) \
            .order_by(Registration.timestamp_start.desc())

        if latest:
            response = [registrations.first()]
        else:
            response = registrations.all()

        return [r.serialize() for r in response]

    def post(self):
        data = json.loads(request.data.decode())
        user_id = db.session.query(User).one().id
        timestamp_now = ts_to_unix(pytz.utc.localize(datetime.datetime.utcnow()))

        # TODO : check if input is logical wrt what exists in the db

        previous_registration = db.session \
            .query(Registration) \
            .filter(Registration.user_id == user_id) \
            .order_by(Registration.timestamp_start.desc()) \
            .first()

        if previous_registration is not None and previous_registration.timestamp_end is None:
            previous_registration.timestamp_end = timestamp_now
            previous_registration.elapsed = timestamp_now - previous_registration.timestamp_start

        if data["active"]:
            new_registration = Registration(
                user_id=user_id,
                action_id=data["id"],
                timestamp_start=timestamp_now
            )
            db.session.add(new_registration)

        db.session.commit()
        return {}


class Stats(Resource):
    def get(self):
        agg_opt = namedtuple("AGGREGATE", "DAY MONTH")("day", "month")

        aggregate_by = request.args.get("aggregate_by", agg_opt.DAY)
        timezone = request.args.get("timezone", "Europe/Brussels")

        # create variables for different aggregation possibilities
        # - timestamp_limit: only take history starting from this timestamp
        # - split_range: a range of timestamps that can be used to split registrations spanning multiple time units
        # - agg_func: function to create the keys on which aggregation will be performed
        if aggregate_by == agg_opt.DAY:
            timestamp_limit = datetime.datetime.utcnow() - datetime.timedelta(days=30)
            timestamp_limit = pytz.timezone(timezone).localize(datetime.datetime(timestamp_limit.year,
                                                                                 timestamp_limit.month,
                                                                                 timestamp_limit.day))
            split_range = [
                ts_to_unix(ts)
                for ts
                in pd.date_range(timestamp_limit,
                                 pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(timezone)),
                                 freq="1D")
            ]
            timestamp_limit = ts_to_unix(timestamp_limit)

            def agg_func(ts):
                try:
                    return unix_to_ts(ts).astimezone(pytz.timezone(timezone)).date().isoformat()
                except ValueError:
                    return ts

        elif aggregate_by == agg_opt.MONTH:
            timestamp_limit = datetime.datetime.utcnow() - datetime.timedelta(days=365)
            timestamp_limit = pytz.timezone(timezone).localize(datetime.datetime(timestamp_limit.year,
                                                                                 timestamp_limit.month,
                                                                                 1))
            split_range = [
                ts_to_unix(ts)
                for ts
                in pd.date_range(timestamp_limit,
                                 pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone(timezone)),
                                 freq="1MS")
            ]
            timestamp_limit = ts_to_unix(timestamp_limit)

            def agg_func(ts):
                try:
                    ts = unix_to_ts(ts).astimezone(pytz.timezone(timezone)).date()
                    return datetime.date(ts.year, ts.month, 1).isoformat()
                except ValueError:
                    return ts

        else:
            timestamp_limit = None
            agg_func = None
            split_range = None
            abort(requests.codes.bad_request)

        # get data into a pandas dataframe
        # TODO filter by user / limit to active user only
        # we must rename "name" to "action", otherwise this conflicts with a dataframe variable
        query = db.session \
            .query(Registration.timestamp_start, Registration.timestamp_end,
                   Registration.elapsed, Action.name.label("action")) \
            .join(Action) \
            .filter(Registration.timestamp_start > timestamp_limit)

        registrations = pd.read_sql(query.statement, db.session.bind)

        # create aggregation key
        registrations["key"] = registrations["timestamp_start"].apply(agg_func)
        registrations["key_end"] = registrations["timestamp_end"].apply(agg_func)

        # split registrations that span several time units
        new_registrations = []
        registrations_to_split = registrations[registrations["key"] != registrations["key_end"]]
        for _, reg in registrations_to_split.iterrows():
            idx = [ts for ts in split_range if reg.timestamp_start < ts < reg.timestamp_end]
            for idx_start, idx_end in zip([reg.timestamp_start] + idx,
                                          idx + [reg.timestamp_end]):
                if pd.isna(idx_end):
                    idx_end = ts_to_unix(pytz.utc.localize(datetime.datetime.utcnow()))
                new_registrations.append({
                    "action": reg.action,
                    "timestamp_start": idx_start,
                    "timestamp_end": idx_end,
                    "key": agg_func(idx_start),
                    "key_end": agg_func(idx_end),
                    "elapsed": idx_end - idx_start,
                })

        registrations = pd.concat([
            registrations[registrations["key"] == registrations["key_end"]],
            pd.DataFrame(data=new_registrations)
        ])

        # drop any registrations that are not complete yet
        registrations = registrations.dropna()

        # aggregate stats
        registrations = registrations[["key", "action", "elapsed"]]
        registrations = registrations.groupby(["key", "action"]).sum().reset_index()

        return [{"key": r.key, "action": r.action, "duration": r.elapsed} for idx, r in registrations.iterrows()]


api.add_resource(ResourceUserList, '/api/user')
api.add_resource(ResourceAction, '/api/action')
api.add_resource(ResourceRegistration, '/api/registration')
api.add_resource(Stats, '/api/stats')


@app.after_request
def set_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


if __name__ == '__main__':
    app.run()
