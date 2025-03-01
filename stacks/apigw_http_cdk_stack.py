# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
from aws_cdk import (
    Stack,
    aws_apigatewayv2 as apigw_v2,
    aws_apigatewayv2_integrations as integrations,
    aws_dynamodb as dynamodb_,
    aws_lambda as lambda_,
    CfnOutput
)
from constructs import Construct

TABLE_NAME_PRODUCTS = "products"
TABLE_NAME_STOCKS = "stocks"

class ApigwHttpCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDb Tables. Default removal policy is RETAIN (`cdk destroy` will not remove these tables)
        product_table = dynamodb_.Table(
            self,
            TABLE_NAME_PRODUCTS,
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            ),
        )
        stock_table = dynamodb_.Table(
            self,
            TABLE_NAME_STOCKS,
            partition_key=dynamodb_.Attribute(
                name="id", type=dynamodb_.AttributeType.STRING
            ),
        )

        # Create the Lambda function to receive the request
        api_hanlder_product_list = lambda_.Function(
            self,
            "getProductList",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda"),
            handler="product_list.handler",
            environment={
                'TABLE_NAME_PRODUCTS': product_table.table_name,
                'TABLE_NAME_STOCKS': stock_table.table_name,
            },
        )

        # Create the Lambda function to receive the request
        api_hanlder_product_by_id = lambda_.Function(
            self,
            "getProductById",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("lambda"),
            handler="product_by_id.handler",
            environment={
                'TABLE_NAME_PRODUCTS': product_table.table_name,
                'TABLE_NAME_STOCKS': stock_table.table_name,
            },
        )

        # Grant permission to lambda to write to demo table
        product_table.grant_read_data(api_hanlder_product_list)
        stock_table.grant_read_data(api_hanlder_product_list)

        product_table.grant_read_data(api_hanlder_product_by_id)
        stock_table.grant_read_data(api_hanlder_product_by_id)

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
            path="/products/{product_id}",
            methods=[apigw_v2.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration("ProductByIdIntegration", api_hanlder_product_by_id)
        )
