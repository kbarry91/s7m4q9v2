from app.rate_limiter import TokenBucketRateLimiter 
import time

def test_new_client_can_burst_to_capacity():
    rate_limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1)
    client_id = "test_client"

    # Initially, the client should be able to consume the full capacity
    for _ in range(5):
        assert rate_limiter.allow_request(client_id) is True

    # The next request should be denied as the bucket is empty
    assert rate_limiter.allow_request(client_id) is False

    # After some time, the bucket should refill and allow requests again
    time.sleep(1)  # Wait for the bucket to refill
    assert rate_limiter.allow_request(client_id) is True

def test_each_client_has_an_independent_bucket():
    rate_limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1)
    client_id_1 = "test_client_1"
    client_id_2 = "test_client_2"

    # Consume all tokens for client 1
    for _ in range(5):
        assert rate_limiter.allow_request(client_id_1) is True

    # Client 1 should now be denied
    assert rate_limiter.allow_request(client_id_1) is False

    # Client 2 should still have its own full bucket.
    assert rate_limiter.allow_request(client_id_2) is True