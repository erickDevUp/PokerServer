import redis

r = redis.Redis(
    host='redis-10847.c12.us-east-1-4.ec2.cloud.redislabs.com',
    port=10847,
    password='BW9TAMyWMSYec1LQU48UdKIHh5wyMYq2'
    )
response = r.ping()
