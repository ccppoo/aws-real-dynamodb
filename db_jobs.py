import json

with open("schema.json", mode='r') as fp:
    Schema = json.load(fp)

def create_all_table(DBConnection):
    DBConnection.create_table(
        TableName="members",
        AttributeDefinitions=Schema['members']['AttributeDefinitions'],
        KeySchema=Schema['members']['KeySchema'],
        ProvisionedThroughput=Schema['members']['ProvisionedThroughput']
    )

    DBConnection.create_table(
        TableName="members-credential",
        AttributeDefinitions=Schema['members-credential']['AttributeDefinitions'],
        KeySchema=Schema['members']['KeySchema'],
        ProvisionedThroughput=Schema['members-credential']['ProvisionedThroughput']
    )

    DBConnection.create_table(
        TableName="rooms",
        AttributeDefinitions=Schema['rooms']['AttributeDefinitions'],
        KeySchema=Schema['rooms']['KeySchema'],
        ProvisionedThroughput=Schema['rooms']['ProvisionedThroughput']
    )

    DBConnection.create_table(
        TableName="chats",
        AttributeDefinitions=Schema['chats']['AttributeDefinitions'],
        KeySchema=Schema['chats']['KeySchema'],
        ProvisionedThroughput=Schema['chats']['ProvisionedThroughput']
    )


def get_table_list(DBConnection):
    return [x.name for x in DBConnection.tables.all()]


def get_data(DBConnection):
    table = DBConnection.tables.all()('chats')
    scanresp = table.scan(TableName='chats')
    items = scanresp['Items']
    for x in items:
        print(x)
