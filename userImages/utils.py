from django.core import signing


def generate_expiring_link(original_url, expiration_time):
    expiration_time_str = expiration_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    signed_data = signing.dumps((original_url, expiration_time_str))
    # Append the signed token to the URL as a query parameter
    return signed_data
