from locust import HttpUser, task, between, SequentialTaskSet
#locust -f pdfapp/locusfile.py --host=https://pdfquizmaker.com
#1200 200
class UserBehavior(SequentialTaskSet):
    @task(1)
    def index(self):
        self.client.get("/en/home")
    
    """@task(2)
    def about(self):
        self.client.get("/en/about")"""


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)