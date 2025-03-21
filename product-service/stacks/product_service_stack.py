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
        # Create the Dead Letter Queue (DLQ)
        dlq = sqs.Queue(
            self,
            id=os.getenv('CATALOG_ITEMS_QUEUE') + 'Dlg',
            retention_period=Duration.days(7)
        )
        dead_letter_queue = sqs.DeadLetterQueue(
            max_receive_count=1,
            queue=dlq
        )
        # Create the SQS queue with DLQ setting
        catalogItemsQueue = sqs.Queue(
            self,
            id = os.getenv('CATALOG_ITEMS_QUEUE'),
            dead_letter_queue=dead_letter_queue,
            visibility_timeout = Duration.seconds((LAMBDA_TIMEOUT * 6))
        )

        # Create an SNS topic
        email_topic = sns.Topic(self, "ProductImportEmail",
            display_name="Product Import Notification"
        )
        # Create email subscriptions with filter policies
        email_topic.add_subscription(sns_subs.EmailSubscription(os.getenv('EMAIL_LOW_PRICE'),
            filter_policy={
                "price": sns.SubscriptionFilter.numeric_filter(
                    less_than_or_equal_to=10
                )
            }
        ))
        email_topic.add_subscription(sns_subs.EmailSubscription(os.getenv('EMAIL_HIGH_PRICE'),
            filter_policy={
                "price": sns.SubscriptionFilter.numeric_filter(
                    greater_than=10
                )
            }
        ))

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
        api_hanlder_catalog_batch_process= lambda_.Function(
            self,
            "catalogBatchProcess",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset("lambda"),
            handler="catalog_batch_process.handler",
            environment={
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
    
        # Add the SQS queue as a trigger to the Lambda function
        api_hanlder_catalog_batch_process.add_event_source_mapping(
            "catalogItemsQueueTrigger",
            event_source_arn = catalogItemsQueue.queue_arn,
            batch_size = int(os.getenv('BATCH_SIZE')),
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
        CfnOutput(self, "HttpApiUrl", value=http_api.url, export_name="ProductApiUrl")

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

        # Export value to access from ImportService Stack
        CfnOutput(self, "CatalogItemsQueueArn",
                value=catalogItemsQueue.queue_arn,
                export_name="CatalogItemsQueueArn")
