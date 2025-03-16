import os
from aws_cdk import (
    Stack,
    aws_apigatewayv2 as apigw_v2,
    aws_apigatewayv2_integrations as integrations,
    aws_dynamodb as dynamodb_,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_events,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subs,
    aws_sqs as sqs,
    aws_iam,
    Duration,
    CfnOutput,
)
from constructs import Construct
from dotenv import load_dotenv

load_dotenv()

class ProductServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDb Tables. Default removal policy is RETAIN (`cdk destroy` will not remove these tables)
        product_table = dynamodb_.Table(
            self,
            os.getenv('TABLE_NAME_PRODUCTS'),
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            ),
        )
        stock_table = dynamodb_.Table(
            self,
            os.getenv('TABLE_NAME_STOCKS'),
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            ),
        )

        # Queue with products to be processed after import
        LAMBDA_TIMEOUT = int(os.getenv('LAMBDA_TIMEOUT'))
        catalogItemsQueue = sqs.Queue(
            self,
            id = os.getenv('CATALOG_ITEMS_QUEUE'),
            # dead_letter_queue=dead_letter_queue,
            visibility_timeout = Duration.seconds((LAMBDA_TIMEOUT * 6))
        )
        CfnOutput(self, "QueueUrl", value=catalogItemsQueue.queue_url)

        # Create an SNS topic
        email_topic = sns.Topic(self, "ProductImportEmail",
            display_name="Product Import Notification"
        )
        email_topic.add_subscription(sns_subs.EmailSubscription(os.getenv('EMAIL')))

        # Create the Lambda function to get ProductList
        api_hanlder_product_list = lambda_.Function(
            self,
            "getProductList",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset("lambda"),
            handler="product_list.handler",
            environment={
                'TABLE_NAME_PRODUCTS': product_table.table_name,
                'TABLE_NAME_STOCKS': stock_table.table_name,
            },
        )

        # Create the Lambda function to receive specific product
        api_hanlder_product_by_id = lambda_.Function(
            self,
            "getProductById",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset("lambda"),
            handler="product_by_id.handler",
            environment={
                'TABLE_NAME_PRODUCTS': product_table.table_name,
                'TABLE_NAME_STOCKS': stock_table.table_name,
            },
        )

         # Create the Lambda function to create product
        api_hanlder_product_create = lambda_.Function(
            self,
            "createProduct",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset("lambda"),
            handler="product_create.handler",
            environment={
                'TABLE_NAME_PRODUCTS': product_table.table_name,
                'TABLE_NAME_STOCKS': stock_table.table_name,
            },
        )

         # Create the Lambda function to process products from queue
        BATCH_SIZE = os.getenv('BATCH_SIZE')
        api_hanlder_catalog_batch_process= lambda_.Function(
            self,
            "catalogBatchProcess",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset("lambda"),
            handler="catalog_batch_process.handler",
            environment={
                'BATCH_SIZE': BATCH_SIZE,
                'SQS_QUEUE_URL': catalogItemsQueue.queue_url,
                'TABLE_NAME_PRODUCTS': product_table.table_name,
                'TABLE_NAME_STOCKS': stock_table.table_name,
                "SNS_TOPIC_ARN": email_topic.topic_arn,
            },
            timeout = Duration.seconds(LAMBDA_TIMEOUT)
        )

        # Grant permission to lambda to read/write to db tables
        product_table.grant_read_data(api_hanlder_product_list)
        stock_table.grant_read_data(api_hanlder_product_list)

        product_table.grant_read_data(api_hanlder_product_by_id)
        stock_table.grant_read_data(api_hanlder_product_by_id)

        product_table.grant_read_write_data(api_hanlder_product_create)
        stock_table.grant_read_write_data(api_hanlder_product_create)

        product_table.grant_read_write_data(api_hanlder_catalog_batch_process)
        stock_table.grant_read_write_data(api_hanlder_catalog_batch_process)
        catalogItemsQueue.grant_consume_messages(api_hanlder_catalog_batch_process)
        email_topic.grant_publish(api_hanlder_catalog_batch_process)

        # Retirve role from Import Stack for lambda function parse_file
        existing_role = aws_iam.Role.from_role_arn(
            self, "ExistingRole", 
            role_arn=os.getenv('PARSE_FILE_LAMBDA_ROLE_ARN'))
        # Define the queue policy to allow messages from the Lambda function's role only
        policy = aws_iam.PolicyStatement(
            actions=['sqs:SendMessage', 'sqs:GetQueueUrl','sqs:ListQueues'],
            effect=aws_iam.Effect.ALLOW,
            principals=[aws_iam.ArnPrincipal(existing_role.role_arn)],
            resources=[catalogItemsQueue.queue_arn]
        )
        catalogItemsQueue.add_to_resource_policy(policy)
    
        # Add the SQS queue as a trigger to the Lambda function
        api_hanlder_catalog_batch_process.add_event_source_mapping(
            "catalogItemsQueueTrigger",
            event_source_arn = catalogItemsQueue.queue_arn,
            batch_size = int(BATCH_SIZE),
        )

        # Create HTTP API
        http_api = apigw_v2.HttpApi(
            self, "Product API",
            create_default_stage=True,  # This creates the $default stage
            cors_preflight=apigw_v2.CorsPreflightOptions(
                allow_methods=[apigw_v2.CorsHttpMethod.ANY],
                allow_origins=['*'],
                allow_headers=['*']
            )
        )

        # Add development stage
        apigw_v2.HttpStage(self, "DevStage",
            http_api=http_api,
            stage_name="development",
            auto_deploy=True
        )

        # Output the API URL
        CfnOutput(self, "HttpApiUrl", value=http_api.url)

        # Adding a route
        http_api.add_routes(
            path="/products",
            methods=[apigw_v2.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration("ProductListIntegration", api_hanlder_product_list)
        )
        http_api.add_routes(
            path="/products",
            methods=[apigw_v2.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration("CreateProductIntegration", api_hanlder_product_create)
        )
        http_api.add_routes(
            path="/products/{product_id}",
            methods=[apigw_v2.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration("ProductByIdIntegration", api_hanlder_product_by_id)
        )
