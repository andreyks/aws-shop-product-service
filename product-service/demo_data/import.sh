
# For initial import please execute command `(cd demo_data; sh import.sh)`

aws dynamodb batch-write-item \
    --request-items file://products.json \
    --return-consumed-capacity INDEXES \
    --return-item-collection-metrics SIZE


aws dynamodb batch-write-item \
    --request-items file://stocks.json \
    --return-consumed-capacity INDEXES \
    --return-item-collection-metrics SIZE
