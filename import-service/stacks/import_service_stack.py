import os
from aws_cdk import (
    Stack,
    aws_apigatewayv2 as apigw_v2,
    aws_apigatewayv2_integrations as integrations,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_s3_notifications as s3n,
    CfnOutput,
    Fn,
    aws_sqs as sqs,
    aws_apigatewayv2_authorizers as authorizers,
    Duration,
)
from constructs import Construct
from dotenv import load_dotenv

load_dotenv()

class ImportServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket. Default removal_policy=RemovalPolicy.RETAIN
        bucket = s3.Bucket(self, "ImportBucket",
            bucket_name = os.getenv('BUCKET_NAME'),
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            block_public_access = s3.BlockPublicAccess.BLOCK_ALL,
            cors=[
                s3.CorsRule(
                    allowed_headers=["*"],
                    allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.GET, s3.HttpMethods.DELETE],
                    allowed_origins=[f"https://{Fn.import_value('DistributionDomain')}"],
                )
            ]
        )

        ## Import products file
        # Create the Lambda function to import product csv file
        import_product_file = lambda_.Function(
            self,
            "importFile",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset("lambda"),
            handler="import_file.handler",
            environment={
                "BUCKET_NAME": bucket.bucket_name
            },
        )
        # Grant the Lambda function permission to generate presigned URLs
        import_product_file.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:PutObject"],
            resources=[bucket.arn_for_objects("*")]
        ))
        # Grant the Lambda function permission to read the bucket
        bucket.grant_read(import_product_file)

        # Import queue from Product Stack
        queueArn = Fn.import_value('CatalogItemsQueueArn')
        importedCatalogItemsQueue = sqs.Queue.from_queue_arn(
            self, 'ImportedCatalogItemsQueue', queueArn
        )

        ## Parse product file
        parse_product_file = lambda_.Function(
            self,
            "parseFile",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset("lambda"),
            handler="parse_file.handler",
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                'QUEUE_URL': importedCatalogItemsQueue.queue_url,
            },
        )
        # Grant the Lambda function permission to read the bucket
        bucket.grant_put(parse_product_file)
        bucket.grant_read_write(parse_product_file)
        bucket.grant_delete(parse_product_file)
        # Add S3 event notification to trigger the process function
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(parse_product_file),
            s3.NotificationKeyFilter(prefix="uploaded/"),
        )
        importedCatalogItemsQueue.grant_send_messages(parse_product_file)

        # Import Authorization Lambda from Authorization Stack
        lambdaArn = Fn.import_value('AuthorizerLambdaArn')
        importedAuthorizerLambda = lambda_.Function.from_function_arn(
            self, 'ImportedAuthorizerLambda', lambdaArn
        )
         # Create the Lambda authorizer
        basic_authorizer = authorizers.HttpLambdaAuthorizer(
            "BasicAuthorizer",
            importedAuthorizerLambda,
            response_types=[authorizers.HttpLambdaResponseType.IAM], # .SIMPLE is recomended die to performance.
            # authorization_type=authorizers.HttpLambdaAuthorizationType.TOKEN,
            identity_source=["$request.header.Authorization"],
            results_cache_ttl=Duration.seconds(0),
        )

        # Create HTTP API
        http_api = apigw_v2.HttpApi(
            self, "Import API",
            create_default_stage=True,  # This creates the $default stage
            cors_preflight=apigw_v2.CorsPreflightOptions(
                allow_methods=[apigw_v2.CorsHttpMethod.ANY],
                allow_origins=[f"https://{Fn.import_value('DistributionDomain')}"],
                allow_headers=['*'],
                allow_credentials=True,
            ),
        )
        # Add development stage
        apigw_v2.HttpStage(self, "DevStage",
            http_api=http_api,
            stage_name="development",
            auto_deploy=True
        )
        # Output the API URL
        CfnOutput(self, "HttpApiUrl", value=http_api.url, export_name='ImportApiUrl')

        # Adding a route
        http_api.add_routes(
            path="/import",
            methods=[apigw_v2.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration("ImportIntegration", import_product_file),
            authorizer=basic_authorizer,
        )
        # importedAuthorizerLambda.grant_invoke(iam.ServicePrincipal("apigateway.amazonaws.com"))
