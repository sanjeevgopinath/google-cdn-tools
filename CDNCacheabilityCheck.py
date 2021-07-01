# Author: Sanjeev Gopinath

# This script is useful for identifying CDN Cacheability of objects stored in Google Cloud Storage
# - Gets cache control, content-type settings from object metadata
# - Gets cache control, content-type settings as observed by response to a HEAD request to Object's public URL
# The Results are stored in Results.csv file

# WARNING:
# ---------
# 1. Not tested for production use.
# 2. May incur charges for
#    - Storage Class A Operations (list buckets, list objects)
#    - Network Egress (head request against every object)


from google.cloud import storage

import pandas as pd
import requests, json


storage_client = storage.Client()
buckets = storage_client.list_buckets()

bucket_list = []
blob_list = []
url_list = []
blob_metadata_cache_control_list = []
blob_metadata_content_type_list = []

response_content_type_list = []
response_cache_control_list = []

blob_count = 0

for bucket in buckets:
    blobs = storage_client.list_blobs(bucket.name)

    for blob in blobs:
        
        # Ignore folders
        if(blob.name.endswith("/")):
            print("Found Folder {}".format(blob.name))
            continue
        
        blob_count = blob_count + 1
        print("Processing Object #{}".format(blob_count))

        if(bucket.name != ""):
            bucket_list.append(bucket.name)
        else:
            bucket_list.append("Unknown")

        if(blob.name != ""):
            blob_list.append(blob.name)
        else:
            blob_list.append("Unknown")

        # Cache Control from Metadata
        if(blob.cache_control != ""):
            blob_metadata_cache_control_list.append(blob.cache_control)
        else:
            blob_metadata_cache_control_list.append("Not Set")
        
        # Content Type from Metadata
        if(blob.content_type != ""):
            blob_metadata_content_type_list.append(blob.content_type)
        else:
            blob_metadata_content_type_list.append("Not Set")

        # Constructing the URL using Bucket name and Blob Name
        blob_url = "https://storage.googleapis.com/{}/{}".format(bucket.name,blob.name)  
        url_list.append(blob_url)

        # HTTP request to retrieve headers. equivalent of CURL -I
        response = requests.head(blob_url)
        response_header = dict(response.headers)

        # Content-Type from Response
        if(response_header.has_key('Content-Type')):
            response_content_type_list.append(response_header['Content-Type'])
        else:
            response_content_type_list.append("Not Set")
        
        # Cache-Control from Response
        if(response_header.has_key('Cache-Control')):
            response_cache_control_list.append(response_header['Cache-Control'])
        else:
            response_cache_control_list.append("Not Set")

print("\nCompleted. Total Number of Objects Processed: {}".format(blob_count))

table = {
    'Object-Name': blob_list,
    'Bucket-Name': bucket_list,
    'Origin-URL': url_list,
    'Response-Cache-Control': response_cache_control_list,
    'Response-Content-Type': response_content_type_list,
    'Metadata-Cache-Control': blob_metadata_cache_control_list,
    'Metadata-Content-Type': blob_metadata_content_type_list
}

results_tbl = pd.DataFrame(table)

results_tbl.to_csv("Results.csv")
