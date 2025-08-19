from dynaconf import Dynaconf

settings = Dynaconf(settings_files=["configs/settings.yaml"], environment=True)
