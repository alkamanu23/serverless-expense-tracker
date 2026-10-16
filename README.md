# Serverless Expense Tracker

A serverless app where users upload a receipt and the expense details (vendor, total, date) are extracted automatically with Amazon Textract, removing manual data entry.

## Architecture

1. User signs in with **Amazon Cognito** and receives a JWT.
2. `POST /receipts` (API Gateway + Lambda) returns a short-lived presigned **S3** upload URL.
3. The receipt is uploaded to S3, which triggers a Lambda function.
4. The function calls **Textract AnalyzeExpense** and saves the parsed result to **DynamoDB**.
5. `GET /expenses` returns the signed-in user's expenses.

All endpoints are protected by a Cognito JWT authorizer. Each Lambda function has its own least-privilege IAM permissions.

## Tech stack

Python 3.12, AWS Lambda, API Gateway (HTTP API), S3, Textract, DynamoDB, Cognito, IAM, AWS SAM

## Deploy

Requires an AWS account, the AWS CLI and the AWS SAM CLI.

```bash
sam build
sam deploy --guided
```

Note the `ApiUrl`, `UserPoolId` and `UserPoolClientId` outputs.

## Try it

```bash
# 1. Create a user
aws cognito-idp sign-up --client-id <ClientId> --username you@example.com --password '<Password>'
aws cognito-idp admin-confirm-sign-up --user-pool-id <PoolId> --username you@example.com

# 2. Get a token
aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id <ClientId> \
  --auth-parameters USERNAME=you@example.com,PASSWORD='<Password>'

# 3. Request an upload URL (use the IdToken)
curl -X POST <ApiUrl>/receipts -H "Authorization: <IdToken>" \
  -H "Content-Type: application/json" -d '{"contentType":"image/jpeg"}'

# 4. Upload the receipt to the returned uploadUrl
curl -X PUT -H "Content-Type: image/jpeg" --data-binary @receipt.jpg "<uploadUrl>"

# 5. List expenses
curl <ApiUrl>/expenses -H "Authorization: <IdToken>"
```

## Clean up

```bash
sam delete
```

## Notes

Rebuilt as a clean portfolio version of a university cloud project, with AI-assisted code that I reviewed and deployed myself.
