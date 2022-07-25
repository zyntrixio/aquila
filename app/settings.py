from environs import Env

env = Env()
env.read_env()


PROJECT_NAME: str = env("PROJECT_NAME", "aquila")
POLARIS_BASE_URL: str = env.url("POLARIS_BASE_URL", "http://polaris-api/loyalty").geturl()
