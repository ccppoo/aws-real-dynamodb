from faker import Faker
import uuid
import random
import datetime
from datetime import timedelta, tzinfo
from pprint import pprint
__all__ = [
    "put_test_member",
    "put_test_member_credentials",
    "put_test_room",
    "put_test_chats",
    "make_test_data"
]

# uuid1 -> time based
# uuid4 -> random

fake = Faker('ko-KR')

class TZ_ko(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=9)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "+09:00"

    def __repr__(self):
        return f"{self.__class__.__name__}()"

def gen_members(count : int):

    basetime = datetime.datetime.now(tz=TZ_ko()).replace(microsecond=0)
    basetime -= datetime.timedelta(
                    days=random.randint(1,count*5), 
                    hours=random.randint(0, count*5),
                    minutes=random.randint(0, count*5)
                )

    items = []
    
    faked_id = [f"{fake.word()}{random.randint(1,999)}" for _ in range(count)]
    faked_NAME = [fake.name() for _ in range(count)]
    faked_nickname = [f"{fake.word()}_{fake.word()}" for _ in range(count)]
    faked_uuid = [uuid.uuid5(uuid.NAMESPACE_OID, name) for name in faked_NAME]
    faked_create_date = [
        basetime - datetime.timedelta(
        days=random.randint(1, count*5),
        hours=random.randint(0, count*5),
        minutes=random.randint(0, count*5)
        ) for _ in range(count)
    ]
    faked_email = [fake.email() for _ in range(count)]
    faked_password = [f'{fake.word()}123' for _ in range(count)]
    
    tt = zip(faked_id,
            faked_NAME,
            faked_nickname,
            faked_uuid,
            faked_create_date,
            faked_email,
            faked_password)

    for i1, i2, i3, i4, i5, i6, i7 in tt:
        items.append({
            "id" : i1,
            "member_name" : i2,
            "member_nickname" : i3,
            "member_uuid" : str(i4),
            "leaved_at" : None,
            "created_at": int(i5.timestamp()),
            "email" : i6,
            "password" : i7
        })
    return items


def gen_chat(members, count: int):

    items = dict()

    ## faking TIME
    TIME_EXTENtion = 30

    basetime = datetime.datetime.now(tz=TZ_ko()).replace(microsecond=0)
    basetime -= datetime.timedelta(minutes=count * TIME_EXTENtion)

    timespan = [1 for _ in range(count)]

    for _ in range(TIME_EXTENtion-1):
        idice = random.choices([i for i in range(count)], k=count)
        for idx in idice:
            timespan[idx] += 1
    assert count * TIME_EXTENtion == sum(timespan)

    faked_TIME = []
    for sec in timespan:
        faked_TIME.append(basetime)
        basetime += timedelta(minutes=sec)

    ## faking NAME
    faked_members = [
        {
            "member_nickname": mem['member_nickname'],
            "member_uuid": mem["member_uuid"],
        } 
        for mem in members
    ]

    ## faking chats
    for f_time in faked_TIME:
        f_mem = random.choice(faked_members)
        f_chat = fake.catch_phrase()    # .text(), .paragraph() 사용 가능(영어)
        f_time_formated = f_time.strftime('%Y-%m-%d %H:%M:%S')
        
        time_sep = f_time.strftime('%Y-%m-%d')
        # 날짜(문자열 -> Int)
        time_sep = int(f_time.replace(hour=0, minute=0, second=0).timestamp())
        time_sep = str(time_sep)
        if items.get(time_sep, None):
            items[time_sep].append({
                "timestamp" : int(f_time.timestamp()),
                "member_name": f_mem['member_nickname'],
                "member_uuid": f_mem['member_uuid'],
                "content": f_chat,
                "media_type": 1,
                "message_state": 1
            })
        else:
            items[time_sep] = [{
                "timestamp": int(f_time.timestamp()),
                "member_name": f_mem['member_nickname'],
                "member_uuid": f_mem['member_uuid'],
                "content": f_chat,
                "media_type": 1,
                "message_state": 1
            }]
    return items


def gen_room(member):
    room_name = fake.word()
    room_uuid = uuid.uuid5(uuid.NAMESPACE_OID, room_name)

    create_time = datetime.datetime.now(tz=TZ_ko()).replace(microsecond=0)
    create_time -= datetime.timedelta(minutes=60)
    create_time_formated = create_time.strftime('%Y-%m-%d %H:%M:%S')

    member_uuid = [
        x['member_uuid'] for x in member
    ]

    return {
        "room_uuid": str(room_uuid),
        "room_name": room_name,
        "created": int(create_time.timestamp()),
        "members": member_uuid
    }


def put_test_member(DBConnection, mems):
    table = DBConnection.Table('members')
    for x in mems:
        item = {
            "member-uuid": x['member_uuid'],
            "id":  x['id'],
            "member-name":  x['member_name'],
            "member-nickname": x["member_nickname"],
            "leaved-at": None,
            "created-at": x['created_at']
        }
        table.put_item(
            Item=item
        )


def put_test_member_credentials(DBConnection, mems):
    table = DBConnection.Table('members-credential')
    for x in mems:
        item = {
            "member-uuid": x['member_uuid'],
            "email": x['email'],
            "password": x['password']
        }
        table.put_item(
            Item=item
        )


def put_test_room(DBConnection, room):
    table = DBConnection.Table('rooms')

    aa = [mem_uuid for mem_uuid in room["members"]]

    item = {
        "room-uuid": room['room_uuid'],
        "room-name": room['room_name'],
        "created": room['created'],
        "members": aa
    }
    table.put_item(
        Item=item
    )


def put_test_chats(DBConnection, chats, room_uuid):
    table = DBConnection.Table('chats')
    item = {
        "room-uuid": room_uuid,
        "time-sep": chats
    }
    # pprint(chats)
    table.put_item(
        Item=item
    )

def make_test_data(DBConnection, members : int, chats : int, mocks : int = 1):
    """
        DBConnection : boto3.resource(DYNAMO_DB, ... )
        members (int) : number of members
        chats (int) : number of chats
    """

    for _ in range(mocks):
        mems = gen_members(members)
        rr = gen_room(mems)
        bb = gen_chat(mems, chats)

        put_test_member(DBConnection, mems)
        put_test_member_credentials(DBConnection, mems)
        put_test_room(DBConnection, rr)
        put_test_chats(DBConnection, bb, rr['room_uuid'])
