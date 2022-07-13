# temp

aws command line 테이블 조회

```powershell
aws dynamodb list-tables --endpoint-url http://localhost:8000
```

```powershell
# main.py에서 환경 변수 가져오기
$Env:DEV = 1
docker-compose -f docker-compose.dev.yml --env-file ./.env.dev up
```

# Docs 참고

## boto3 - DynamoDB

https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#id76