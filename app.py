from flask import Flask
import boto3
from dotenv import load_dotenv
import os
from utils import *
from db_jobs import *


app = Flask(__name__)


@app.route('/')
def index():
    return "This is the main page."


@app.route('/room')
def get_items():
    # ddb.table.scan(TableName='chats')
    return 'TODO: Implement Functionality'

if __name__ == '__main__':
    

    if os.environ.get('DEV', 1):
        from gen_test_data import *
        load_dotenv('.env.dev')

    ddb_client = boto3.client(
        DYNAMO_DB,
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=["AWS_SECRET_ACCESS_KEY"]
    )

    ddb = boto3.resource(
        DYNAMO_DB,
        endpoint_url=os.environ["ENDPOINT_URL"],
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=["AWS_SECRET_ACCESS_KEY"]
    )

    # # key 값을 알고 있는 경우

    from pprint import pprint
    def get_room_by_uuid(uuid_ : str):
        response = ddb_client.get_item(
            TableName='rooms',
            Key={
                "room-uuid": {"S": uuid_},
            }
        )
        
        return {
            'created': response['Item']['created']['N'],
            'members': [its['S'] for its in response['Item']['members']['L']],
            'room-name': response['Item']['room-name']['S'],
            'room-uuid': response['Item']['room-uuid']['S']
        }
        
    def get_rooms():
        response = ddb.Table('rooms').scan(
            Select="ALL_ATTRIBUTES")

        return response["Items"]

    def get_rooms_with_member(member_uuid : str):
        response = ddb.Table('rooms').scan(
            Select="ALL_ATTRIBUTES",
            ScanFilter={
                "members":{
                    'AttributeValueList' : [
                        member_uuid
                    ],
                    'ComparisonOperator': 'CONTAINS'
                }
            })
        return [
            item for item in response['Items']
        ]

    def get_chat_in_room(room_uuid : str, count : int):
        '''
        채팅이 일단은 일(day) 별로 구분되어 저장되고 있음
        근데 문제는 쿼리를 해야하는데
        이게 "time-sep" : { ... } 안에 key 형태로 있어서
        딕셔너리 안에 키값을 또 쿼리하는 방법을 모르겠음
        그래서 일단 되는대로 다 주기
        '''
        response = ddb_client.get_item(
            TableName='chats',
            Key={
                "room-uuid": {"S": room_uuid},
                
            },
            AttributesToGet=[
                'time-sep'
            ]
        )

        # for k, v in response["Item"]['time-sep']['M']['1657378800'].items():
        iits = dict()
        for time_sep in sorted(response["Item"]['time-sep']['M'].keys(), key=lambda x: int(x), reverse=True):
            temp_it = []
            for chat in response["Item"]['time-sep']['M'][time_sep]['L']:
                temp_it.append({
                    'content' : chat['M']['content']['S'],
                    'member_name': chat['M']['member_name']['S'],
                    'member_uuid': chat['M']['member_uuid']['S'],
                    'message_state': chat['M']['message_state']['N'],
                    'timestamp': int(chat['M']['timestamp']['N'])
                })
            iits[int(time_sep)] = temp_it
        return iits

    pprint(get_chat_in_room("9f8b6d28-9fb7-5704-9459-8737233c15e9", 50))

    exit()

    create_all_table(ddb)

    if os.environ.get('DEV', 0):
        make_test_data(ddb, 5, 200, 2)


    # port = int(os.environ.get('PORT', 3333))
    # app.run(debug=True, host='localhost', port=port)